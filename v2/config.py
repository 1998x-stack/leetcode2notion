"""
配置管理模块
职责：管理所有配置参数
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class NotionConfig:
    """Notion API 配置"""
    token: str
    root_page_id: str
    max_retries: int = 3
    rate_limit_delay: float = 0.35  # Notion API 限制：3 requests/second
    max_blocks_per_request: int = 100
    
    @classmethod
    def from_env(cls) -> "NotionConfig":
        """从环境变量加载配置"""
        token = os.getenv("NOTION_TOKEN")
        root_page_id = os.getenv("NOTION_ROOT_PAGE_ID")
        
        if not token:
            raise ValueError("NOTION_TOKEN environment variable is required")
        if not root_page_id:
            raise ValueError("NOTION_ROOT_PAGE_ID environment variable is required")
        
        return cls(token=token, root_page_id=root_page_id)


@dataclass
class ScraperConfig:
    """网页抓取配置"""
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0
    rate_limit_delay: float = 1.0  # 避免被封
    
    # CSS 选择器
    description_selector: str = ".gap-1+ div .elfjS"
    topics_selector: str = ".pl-7 .text-text-secondary"
    hints_selector: str = ".transition-all .elfjS"
    similar_questions_selector: str = ".dark\\:hover\\:text-dark-blue-s"


@dataclass
class AppConfig:
    """应用配置"""
    csv_path: str = "leetcode.csv"
    notion_config: NotionConfig = None
    scraper_config: ScraperConfig = None
    
    # 处理选项
    skip_premium: bool = True
    max_problems: Optional[int] = None  # None = 处理所有
    batch_size: int = 10  # 每批处理的问题数
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "leetcode_notion.log"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """从环境变量加载配置"""
        return cls(
            csv_path=os.getenv("LEETCODE_CSV", "leetcode.csv"),
            notion_config=NotionConfig.from_env(),
            scraper_config=ScraperConfig(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_problems=int(os.getenv("MAX_PROBLEMS", "0")) or None,
        )