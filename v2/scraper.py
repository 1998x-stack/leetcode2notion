"""
LeetCode 网页抓取模块
职责：抓取 LeetCode 问题详细信息
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import sys
import time
import traceback
from typing import Optional
import requests
from bs4 import BeautifulSoup
from loguru import logger

from models import LeetCodeProblem, LeetCodeDetail
from config import ScraperConfig


class LeetCodeScraper:
    """LeetCode 网页抓取器"""
    
    def __init__(self, config: ScraperConfig):
        """初始化抓取器"""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
    
    def scrape_problem(self, problem: LeetCodeProblem) -> LeetCodeDetail:
        """
        抓取问题详细信息
        
        Args:
            problem: LeetCode 问题基本信息
            
        Returns:
            问题详细信息
        """
        logger.info(f"抓取问题: {problem.problem_id} - {problem.problem_title}")
        
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)
                
                response = self.session.get(
                    problem.href,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                
                # 检查是否需要订阅
                if "subscribe" in response.text.lower() or "premium" in response.text.lower():
                    # 进一步检查是否真的是 premium
                    if self._is_premium_problem(response.text):
                        logger.warning(f"Premium 问题: {problem.problem_id}")
                        return LeetCodeDetail(
                            is_premium=True,
                            scrape_success=False,
                            scrape_error="Premium problem - subscription required"
                        )
                
                # 解析页面
                detail = self._parse_page(response.text)
                logger.info(f"抓取成功: {problem.problem_id}")
                return detail
                
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.config.max_retries})")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.config.max_retries}): {str(e)}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                    
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.error(f"抓取失败: {error_message}")
                
                return LeetCodeDetail(
                    scrape_success=False,
                    scrape_error=str(exc_value)
                )
        
        # 重试耗尽
        return LeetCodeDetail(
            scrape_success=False,
            scrape_error="Max retries exceeded"
        )
    
    def _is_premium_problem(self, html: str) -> bool:
        """检查是否为 premium 问题"""
        premium_indicators = [
            "locked-question",
            "premium-tag",
            "subscribe to unlock",
            "premium only"
        ]
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in premium_indicators)
    
    def _parse_page(self, html: str) -> LeetCodeDetail:
        """
        解析页面内容
        
        Args:
            html: HTML 内容
            
        Returns:
            问题详细信息
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 抓取描述
        description = self._extract_description(soup)
        
        # 抓取主题标签
        topics = self._extract_topics(soup)
        
        # 抓取提示
        hints = self._extract_hints(soup)
        
        # 抓取相似问题
        similar_questions = self._extract_similar_questions(soup)
        
        return LeetCodeDetail(
            description=description,
            topics=topics,
            hints=hints,
            similar_questions=similar_questions,
            scrape_success=True
        )
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取问题描述"""
        try:
            elements = soup.select(self.config.description_selector)
            if elements:
                # 获取第一个元素的文本
                text = elements[0].get_text(strip=True, separator="\n")
                return text
            return "Description not found"
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取描述失败: {error_message}")
            return "Description extraction failed"
    
    def _extract_topics(self, soup: BeautifulSoup) -> list:
        """提取主题标签"""
        try:
            elements = soup.select(self.config.topics_selector)
            topics = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
            return topics
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取主题失败: {error_message}")
            return []
    
    def _extract_hints(self, soup: BeautifulSoup) -> list:
        """提取提示"""
        try:
            elements = soup.select(self.config.hints_selector)
            hints = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
            return hints
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取提示失败: {error_message}")
            return []
    
    def _extract_similar_questions(self, soup: BeautifulSoup) -> list:
        """提取相似问题"""
        try:
            elements = soup.select(self.config.similar_questions_selector)
            similar = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
            return similar
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"提取相似问题失败: {error_message}")
            return []