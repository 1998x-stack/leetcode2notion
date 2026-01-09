"""
LeetCode Notion 页面创建模块
职责：使用 Notion API 创建 LeetCode 问题页面
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import sys
import time
import traceback
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from notion_client import Client
from notion_client.errors import APIResponseError
from loguru import logger

from leetcode_models import LeetCodeProblem
from leetcode_converter import LeetCodeNotionConverter


@dataclass
class NotionConfig:
    """Notion 配置"""
    token: str
    root_page_id: str
    rate_limit_delay: float = 0.4
    max_retries: int = 3


@dataclass
class CreationResult:
    """创建结果"""
    success: bool
    problem_title: str
    page_id: Optional[str] = None
    page_url: Optional[str] = None
    blocks_created: int = 0
    error: Optional[str] = None


class LeetCodeNotionCreator:
    """
    LeetCode Notion 页面创建器
    
    负责：
    1. 创建 LeetCode 问题页面
    2. 分批添加内容 blocks
    3. 处理速率限制和错误
    """
    
    MAX_BLOCKS_PER_REQUEST = 100
    
    def __init__(
        self,
        config: NotionConfig,
        converter: Optional[LeetCodeNotionConverter] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
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
        
        self.created_count = 0
        self.failed_count = 0
    
    def _report_progress(self, message: str, current: int, total: int):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(message, current, total)
        else:
            percentage = (current / total * 100) if total > 0 else 0
            logger.info(f"[{percentage:.1f}%] {message}")
    
    def _create_page_sync(
        self,
        parent_id: str,
        title: str,
        icon: str,
        blocks: List[Dict]
    ) -> CreationResult:
        """
        同步创建页面（带重试）
        
        Args:
            parent_id: 父页面 ID
            title: 页面标题
            icon: 页面图标
            blocks: 初始 blocks
            
        Returns:
            创建结果
        """
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)
                
                response = self.client.pages.create(
                    parent={"page_id": parent_id},
                    icon={"emoji": icon},
                    properties={
                        "title": [{"text": {"content": title}}]
                    },
                    children=blocks[:self.MAX_BLOCKS_PER_REQUEST]
                )
                
                page_id = response["id"]
                page_url = response.get("url", f"https://notion.so/{page_id.replace('-', '')}")
                
                return CreationResult(
                    success=True,
                    problem_title=title,
                    page_id=page_id,
                    page_url=page_url,
                    blocks_created=len(blocks[:self.MAX_BLOCKS_PER_REQUEST])
                )
                
            except APIResponseError as e:
                logger.warning(f"API 错误 (尝试 {attempt+1}/{self.config.max_retries}): {e.code}, {e.message}")
                
                if e.code == "rate_limited":
                    wait_time = 2 ** attempt
                    logger.info(f"速率限制，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
                
                if e.code == "validation_error":
                    logger.warning("验证错误，尝试不带 blocks 创建...")
                    return self._create_page_sync(parent_id, title, icon, [])
                
                return CreationResult(
                    success=False,
                    problem_title=title,
                    error=f"{e.code}: {e.message}"
                )
                
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.warning(f"请求失败 (尝试 {attempt+1}/{self.config.max_retries}): {error_message}")
                time.sleep(1)
                continue
        
        return CreationResult(
            success=False,
            problem_title=title,
            error="重试次数耗尽"
        )
    
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
                    logger.error(f"追加 blocks 失败: {e.code}, {e.message}")
                    return False
                    
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.warning(f"追加失败 (尝试 {attempt+1}): {error_message}")
                time.sleep(1)
                continue
        
        return False
    
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
        
        for i in range(0, len(blocks), self.MAX_BLOCKS_PER_REQUEST):
            batch = blocks[i:i + self.MAX_BLOCKS_PER_REQUEST]
            
            if self._append_blocks_sync(page_id, batch):
                total_appended += len(batch)
                logger.debug(f"追加 {len(batch)} blocks (总计 {total_appended})")
            else:
                logger.warning(f"批次追加失败: {i} - {i + len(batch)}")
                break
        
        return total_appended
    
    def create_problem_page(
        self,
        problem: LeetCodeProblem,
        parent_id: Optional[str] = None
    ) -> CreationResult:
        """
        创建 LeetCode 问题页面
        
        Args:
            problem: LeetCode 问题
            parent_id: 父页面 ID（默认使用配置中的 root_page_id）
            
        Returns:
            创建结果
        """
        parent_id = parent_id or self.config.root_page_id
        
        logger.info(f"创建问题页面: {problem.display_title}")
        
        try:
            # 转换内容
            blocks = self.converter.convert_problem(problem)
            logger.debug(f"转换完成: {len(blocks)} blocks")
            
            # 确定图标
            icon = problem.difficulty_emoji
            
            # 创建页面（先添加前100个blocks）
            initial_blocks = blocks[:self.MAX_BLOCKS_PER_REQUEST]
            result = self._create_page_sync(
                parent_id,
                problem.display_title,
                icon,
                initial_blocks
            )
            
            if not result.success:
                self.failed_count += 1
                return result
            
            result.blocks_created = len(initial_blocks)
            
            # 追加剩余 blocks
            if len(blocks) > self.MAX_BLOCKS_PER_REQUEST:
                remaining = blocks[self.MAX_BLOCKS_PER_REQUEST:]
                appended = self._append_blocks_batched(result.page_id, remaining)
                result.blocks_created += appended
            
            logger.info(f"问题页面创建成功: {result.page_id} ({result.blocks_created} blocks)")
            
            self.created_count += 1
            
            return result
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"创建问题页面失败: {error_message}")
            self.failed_count += 1
            return CreationResult(
                success=False,
                problem_title=problem.display_title,
                error=error_message
            )
    
    def create_batch(
        self,
        problems: List[LeetCodeProblem],
        skip_failed_scrapes: bool = True
    ) -> List[CreationResult]:
        """
        批量创建问题页面
        
        Args:
            problems: 问题列表
            skip_failed_scrapes: 是否跳过抓取失败的问题
            
        Returns:
            创建结果列表
        """
        results = []
        total = len(problems)
        
        for i, problem in enumerate(problems):
            # 跳过抓取失败的问题
            if skip_failed_scrapes and not problem.scrape_success:
                logger.info(f"跳过抓取失败的问题: {problem.display_title}")
                results.append(CreationResult(
                    success=False,
                    problem_title=problem.display_title,
                    error="Scrape failed"
                ))
                continue
            
            self._report_progress(
                f"创建 {problem.display_title}",
                i + 1,
                total
            )
            
            result = self.create_problem_page(problem)
            results.append(result)
        
        logger.info(f"批量创建完成: {self.created_count} 成功, {self.failed_count} 失败")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "created_count": self.created_count,
            "failed_count": self.failed_count,
            "success_rate": f"{(self.created_count / (self.created_count + self.failed_count) * 100):.1f}%" if (self.created_count + self.failed_count) > 0 else "0%"
        }