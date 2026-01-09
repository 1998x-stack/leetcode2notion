"""
LeetCode 数据模型
职责：定义所有数据结构
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class LeetCodeProblem:
    """LeetCode 问题基本信息（来自 CSV）"""
    href: str
    question: str
    completion_rate: str
    level: str
    
    @property
    def problem_id(self) -> str:
        """从问题标题提取 ID"""
        return self.question.split('.')[0].strip()
    
    @property
    def problem_title(self) -> str:
        """从问题标题提取标题"""
        parts = self.question.split('.', 1)
        if len(parts) > 1:
            return parts[1].strip()
        return self.question


@dataclass
class LeetCodeDetail:
    """LeetCode 问题详细信息（来自网页抓取）"""
    description: str = ""
    topics: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    similar_questions: List[str] = field(default_factory=list)
    is_premium: bool = False
    scrape_success: bool = True
    scrape_error: Optional[str] = None


@dataclass
class LeetCodeFullData:
    """完整的 LeetCode 问题数据"""
    problem: LeetCodeProblem
    detail: Optional[LeetCodeDetail] = None
    
    @property
    def has_detail(self) -> bool:
        """是否有详细信息"""
        return self.detail is not None and self.detail.scrape_success


@dataclass
class NotionPageResult:
    """Notion 页面创建结果"""
    success: bool
    problem_id: str
    problem_title: str
    page_id: Optional[str] = None
    page_url: Optional[str] = None
    blocks_created: int = 0
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessStats:
    """处理统计信息"""
    total_problems: int = 0
    scraped_success: int = 0
    scraped_failed: int = 0
    premium_problems: int = 0
    pages_created: int = 0
    pages_failed: int = 0
    total_blocks: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def get_duration(self) -> float:
        """获取处理时长（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "total_problems": self.total_problems,
            "scraped_success": self.scraped_success,
            "scraped_failed": self.scraped_failed,
            "premium_problems": self.premium_problems,
            "pages_created": self.pages_created,
            "pages_failed": self.pages_failed,
            "total_blocks": self.total_blocks,
            "duration_seconds": self.get_duration(),
            "success_rate": f"{self.pages_created / self.total_problems * 100:.1f}%" if self.total_problems > 0 else "0%"
        }