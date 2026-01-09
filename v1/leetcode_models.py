"""
LeetCode 数据模型
职责：定义 LeetCode 问题的数据结构
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Difficulty(Enum):
    """题目难度"""
    EASY = "Easy"
    MEDIUM = "Med."
    HARD = "Hard"
    
    @classmethod
    def from_string(cls, value: str) -> "Difficulty":
        """从字符串转换"""
        mapping = {
            "easy": cls.EASY,
            "med.": cls.MEDIUM,
            "medium": cls.MEDIUM,
            "hard": cls.HARD,
        }
        return mapping.get(value.lower(), cls.MEDIUM)
    
    def get_emoji(self) -> str:
        """获取难度对应的 emoji"""
        return {
            self.EASY: "🟢",
            self.MEDIUM: "🟡",
            self.HARD: "🔴",
        }[self]
    
    def get_color(self) -> str:
        """获取 Notion 颜色"""
        return {
            self.EASY: "green_background",
            self.MEDIUM: "yellow_background",
            self.HARD: "red_background",
        }[self]


@dataclass
class SimilarQuestion:
    """相似问题"""
    title: str
    url: str
    difficulty: Optional[Difficulty] = None


@dataclass
class LeetCodeProblem:
    """LeetCode 问题完整数据"""
    # CSV 基础信息
    number: str
    title: str
    href: str
    completion_rate: str
    difficulty: Difficulty
    
    # 抓取的详细信息
    description: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    similar_questions: List[SimilarQuestion] = field(default_factory=list)
    
    # 状态信息
    scrape_success: bool = False
    error_message: Optional[str] = None
    requires_subscription: bool = False
    
    @property
    def display_title(self) -> str:
        """显示标题（包含编号）"""
        return f"{self.number}. {self.title}"
    
    @property
    def difficulty_emoji(self) -> str:
        """难度 emoji"""
        return self.difficulty.get_emoji()
    
    @property
    def completion_percentage(self) -> float:
        """完成率（数值）"""
        try:
            return float(self.completion_rate.rstrip('%'))
        except:
            return 0.0
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "number": self.number,
            "title": self.title,
            "href": self.href,
            "completion_rate": self.completion_rate,
            "difficulty": self.difficulty.value,
            "description": self.description,
            "topics": self.topics,
            "hints": self.hints,
            "similar_questions": [
                {"title": sq.title, "url": sq.url, "difficulty": sq.difficulty.value if sq.difficulty else None}
                for sq in self.similar_questions
            ],
            "scrape_success": self.scrape_success,
            "error_message": self.error_message,
            "requires_subscription": self.requires_subscription,
        }


@dataclass
class ScrapingStats:
    """抓取统计信息"""
    total_problems: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    subscription_required: int = 0
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_problems == 0:
            return 0.0
        return (self.successful_scrapes / self.total_problems) * 100
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "total_problems": self.total_problems,
            "successful_scrapes": self.successful_scrapes,
            "failed_scrapes": self.failed_scrapes,
            "subscription_required": self.subscription_required,
            "success_rate": f"{self.get_success_rate():.1f}%",
        }