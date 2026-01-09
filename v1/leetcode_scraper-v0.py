"""
LeetCode 网页抓取模块
职责：从 LeetCode 网页提取问题详细信息
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import sys
import time
import traceback
from typing import List, Optional, Callable
import requests
from bs4 import BeautifulSoup
from loguru import logger

from leetcode_models import LeetCodeProblem, SimilarQuestion, Difficulty


class LeetCodeScraper:
    """
    LeetCode 网页抓取器
    
    负责：
    1. 从 LeetCode 页面提取问题详情
    2. 处理需要订阅的页面
    3. 错误处理和重试
    """
    
    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        rate_limit_delay: float = 1.0,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ):
        """
        初始化抓取器
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            rate_limit_delay: 请求间隔（秒）
            progress_callback: 进度回调函数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.progress_callback = progress_callback
        
        # 设置请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _report_progress(self, message: str, current: int, total: int):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(message, current, total)
        else:
            percentage = (current / total * 100) if total > 0 else 0
            logger.info(f"[{percentage:.1f}%] {message}")
    
    def scrape_problem(self, problem: LeetCodeProblem) -> bool:
        """
        抓取单个问题的详细信息
        
        Args:
            problem: LeetCode 问题对象（将被修改）
            
        Returns:
            是否成功抓取
        """
        logger.info(f"抓取问题: {problem.display_title}")
        
        for attempt in range(self.max_retries):
            try:
                # 速率限制
                if attempt > 0:
                    time.sleep(self.rate_limit_delay * (2 ** attempt))
                else:
                    time.sleep(self.rate_limit_delay)
                
                # 发送请求
                response = self.session.get(
                    problem.href,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code} for {problem.href}")
                    continue
                
                # 解析页面
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 检查是否需要订阅
                if self._check_subscription_required(soup, response.text):
                    problem.requires_subscription = True
                    problem.error_message = "Requires LeetCode Premium subscription"
                    logger.warning(f"需要订阅: {problem.display_title}")
                    return False
                
                # 提取信息
                problem.description = self._extract_description(soup)
                problem.topics = self._extract_topics(soup)
                problem.hints = self._extract_hints(soup)
                problem.similar_questions = self._extract_similar_questions(soup)
                
                problem.scrape_success = True
                logger.info(f"成功抓取: {problem.display_title}")
                return True
                
            except requests.Timeout:
                logger.warning(f"超时 (尝试 {attempt + 1}/{self.max_retries}): {problem.href}")
                continue
                
            except requests.RequestException as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.warning(f"请求错误 (尝试 {attempt + 1}/{self.max_retries}): {error_message}")
                continue
                
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.error(f"解析错误: {error_message}")
                problem.error_message = str(exc_value)
                return False
        
        problem.error_message = "重试次数耗尽"
        return False
    
    def _check_subscription_required(self, soup: BeautifulSoup, html: str) -> bool:
        """检查是否需要订阅"""
        # 检查常见的订阅标识
        subscription_indicators = [
            "premium",
            "subscribe",
            "locked",
            "upgrade to unlock",
        ]
        
        html_lower = html.lower()
        for indicator in subscription_indicators:
            if indicator in html_lower:
                return True
        
        # 检查锁图标或类似标识
        lock_elements = soup.find_all(['svg', 'i', 'span'], class_=lambda x: x and 'lock' in x.lower())
        if lock_elements:
            return True
        
        return False
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """提取问题描述"""
        try:
            # 尝试多个可能的选择器
            selectors = [
                '.gap-1+ div .elfjS',
                '[data-track-load="description_content"]',
                '.question-content',
                '[class*="description"]',
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    # 提取文本，清理空白
                    text = elements[0].get_text(separator='\n', strip=True)
                    if text and len(text) > 20:
                        return text
            
            logger.warning("未找到问题描述")
            return None
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取描述失败: {error_message}")
            return None
    
    def _extract_topics(self, soup: BeautifulSoup) -> List[str]:
        """提取主题标签"""
        try:
            # 尝试多个可能的选择器
            selectors = [
                '.pl-7 .text-text-secondary',
                '[class*="topic-tag"]',
                '[class*="tag"]',
            ]
            
            topics = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        text = elem.get_text(strip=True)
                        if text and text not in topics:
                            topics.append(text)
            
            return topics[:20]  # 限制数量
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取主题失败: {error_message}")
            return []
    
    def _extract_hints(self, soup: BeautifulSoup) -> List[str]:
        """提取提示"""
        try:
            # 尝试多个可能的选择器
            selectors = [
                '.transition-all .elfjS',
                '[class*="hint"]',
                '[data-cy*="hint"]',
            ]
            
            hints = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        text = elem.get_text(separator=' ', strip=True)
                        if text and len(text) > 10 and text not in hints:
                            hints.append(text)
            
            return hints[:10]  # 限制数量
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取提示失败: {error_message}")
            return []
    
    def _extract_similar_questions(self, soup: BeautifulSoup) -> List[SimilarQuestion]:
        """提取相似问题"""
        try:
            # 尝试多个可能的选择器
            selectors = [
                '.dark\\:hover\\:text-dark-blue-s',
                '[class*="similar"]',
                'a[href*="/problems/"]',
            ]
            
            similar = []
            seen_urls = set()
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        # 提取链接和标题
                        href = elem.get('href', '')
                        if '/problems/' not in href:
                            continue
                        
                        if not href.startswith('http'):
                            href = 'https://leetcode.com' + href
                        
                        if href in seen_urls:
                            continue
                        
                        title = elem.get_text(strip=True)
                        if not title:
                            continue
                        
                        similar.append(SimilarQuestion(
                            title=title,
                            url=href,
                        ))
                        seen_urls.add(href)
            
            return similar[:10]  # 限制数量
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取相似问题失败: {error_message}")
            return []
    
    def scrape_batch(
        self,
        problems: List[LeetCodeProblem],
        skip_subscription: bool = True
    ) -> int:
        """
        批量抓取问题
        
        Args:
            problems: 问题列表
            skip_subscription: 是否跳过需要订阅的问题
            
        Returns:
            成功抓取的数量
        """
        successful = 0
        total = len(problems)
        
        for i, problem in enumerate(problems):
            self._report_progress(
                f"抓取 {problem.display_title}",
                i + 1,
                total
            )
            
            success = self.scrape_problem(problem)
            
            if success:
                successful += 1
            elif problem.requires_subscription and skip_subscription:
                logger.info(f"跳过订阅问题: {problem.display_title}")
        
        return successful