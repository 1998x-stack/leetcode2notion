"""
Notion 页面创建模块
职责：使用 Notion API 创建 LeetCode 问题页面
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import sys
import time
import traceback
from typing import List, Dict, Any, Optional, Callable
from notion_client import Client
from notion_client.errors import APIResponseError
from loguru import logger

from config import NotionConfig
from models import LeetCodeFullData, NotionPageResult
from notion_blocks import LeetCodeNotionConverter


class LeetCodeNotionCreator:
    """LeetCode Notion 页面创建器"""
    
    def __init__(
        self,
        config: NotionConfig,
        converter: Optional[LeetCodeNotionConverter] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ):
        """
        初始化创建器
        
        Args:
            config: Notion 配置
            converter: 内容转换器
            progress_callback: 进度回调函数
        """
        self.config = config
        self.client = Client(auth=config.token)
        self.converter = converter or LeetCodeNotionConverter()
        self.progress_callback = progress_callback
    
    def create_problem_page(self, data: LeetCodeFullData) -> NotionPageResult:
        """
        创建 LeetCode 问题页面
        
        Args:
            data: LeetCode 完整数据
            
        Returns:
            页面创建结果
        """
        problem = data.problem
        logger.info(f"创建页面: {problem.problem_id} - {problem.problem_title}")
        
        try:
            # 转换为 Notion blocks
            blocks = self.converter.convert_problem(data)
            logger.debug(f"转换完成: {len(blocks)} blocks")
            
            # 确定页面图标
            level_icons = {
                "Easy": "🟢",
                "Med.": "🟡",
                "Hard": "🔴"
            }
            icon = level_icons.get(problem.level, "📝")
            
            # 页面标题
            title = f"{problem.problem_id}. {problem.problem_title}"
            
            # 创建页面
            result = self._create_page_with_blocks(
                title=title,
                icon=icon,
                blocks=blocks
            )
            
            if result.success:
                logger.info(f"页面创建成功: {result.page_id} ({result.blocks_created} blocks)")
            else:
                logger.error(f"页面创建失败: {result.error}")
            
            return result
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"创建页面失败: {error_message}")
            
            return NotionPageResult(
                success=False,
                problem_id=problem.problem_id,
                problem_title=problem.problem_title,
                error=str(exc_value)
            )
    
    def _create_page_with_blocks(
        self,
        title: str,
        icon: str,
        blocks: List[Dict[str, Any]]
    ) -> NotionPageResult:
        """
        创建页面并添加 blocks
        
        Args:
            title: 页面标题
            icon: 页面图标
            blocks: blocks 列表
            
        Returns:
            创建结果
        """
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)
                
                # 创建页面（前100个blocks）
                initial_blocks = blocks[:self.config.max_blocks_per_request]
                
                response = self.client.pages.create(
                    parent={"page_id": self.config.root_page_id},
                    icon={"emoji": icon},
                    properties={
                        "title": [{"text": {"content": title}}]
                    },
                    children=initial_blocks
                )
                
                page_id = response["id"]
                page_url = response.get("url", f"https://notion.so/{page_id.replace('-', '')}")
                blocks_created = len(initial_blocks)
                
                # 追加剩余 blocks
                if len(blocks) > self.config.max_blocks_per_request:
                    remaining = blocks[self.config.max_blocks_per_request:]
                    appended = self._append_blocks_batched(page_id, remaining)
                    blocks_created += appended
                
                return NotionPageResult(
                    success=True,
                    problem_id="",
                    problem_title=title,
                    page_id=page_id,
                    page_url=page_url,
                    blocks_created=blocks_created
                )
                
            except APIResponseError as e:
                logger.warning(f"API 错误 (尝试 {attempt+1}/{self.config.max_retries}): {e.code}")
                
                if e.code == "rate_limited":
                    wait_time = 2 ** attempt
                    logger.info(f"速率限制，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
                
                if e.code == "validation_error":
                    logger.warning("验证错误，尝试不带 blocks 创建...")
                    return self._create_page_with_blocks(title, icon, [])
                
                return NotionPageResult(
                    success=False,
                    problem_id="",
                    problem_title=title,
                    error=f"{e.code}: {e.message}"
                )
                
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.warning(f"请求失败 (尝试 {attempt+1}): {error_message}")
                time.sleep(1)
                continue
        
        return NotionPageResult(
            success=False,
            problem_id="",
            problem_title=title,
            error="重试次数耗尽"
        )
    
    def _append_blocks_batched(self, page_id: str, blocks: List[Dict]) -> int:
        """
        分批追加 blocks
        
        Args:
            page_id: 页面 ID
            blocks: blocks 列表
            
        Returns:
            成功追加的数量
        """
        total_appended = 0
        
        for i in range(0, len(blocks), self.config.max_blocks_per_request):
            batch = blocks[i:i + self.config.max_blocks_per_request]
            
            if self._append_blocks_sync(page_id, batch):
                total_appended += len(batch)
                logger.debug(f"追加 {len(batch)} blocks (总计 {total_appended})")
            else:
                logger.warning(f"批次追加失败: {i} - {i + len(batch)}")
                break
        
        return total_appended
    
    def _append_blocks_sync(self, page_id: str, blocks: List[Dict]) -> bool:
        """
        同步追加 blocks
        
        Args:
            page_id: 页面 ID
            blocks: blocks 列表
            
        Returns:
            是否成功
        """
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)
                
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=blocks
                )
                return True
                
            except APIResponseError as e:
                if e.code == "rate_limited":
                    wait_time = 2 ** attempt
                    logger.warning(f"速率限制，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"追加 blocks 失败: {e.code}")
                    return False
                    
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.warning(f"追加失败 (尝试 {attempt+1}): {error_message}")
                time.sleep(1)
                continue
        
        return False
    
    def report_progress(self, message: str, current: int, total: int):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(message, current, total)
        else:
            percentage = (current / total * 100) if total > 0 else 0
            logger.info(f"[{percentage:.1f}%] {message}")