"""
LeetCode to Notion 主程序
职责：协调所有模块，执行完整的处理流程
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import sys
import csv
import traceback
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from loguru import logger

from config import AppConfig
from models import (
    LeetCodeProblem,
    LeetCodeFullData,
    ProcessStats,
)
from scraper import LeetCodeScraper
from notion_creator import LeetCodeNotionCreator


def setup_logging(config: AppConfig):
    """配置日志"""
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level=config.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    
    # 文件输出
    if config.log_file:
        logger.add(
            config.log_file,
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            rotation="10 MB"
        )


def load_problems_from_csv(csv_path: str) -> List[LeetCodeProblem]:
    """
    从 CSV 文件加载问题列表
    
    Args:
        csv_path: CSV 文件路径
        
    Returns:
        问题列表
    """
    logger.info(f"加载 CSV 文件: {csv_path}")
    
    problems = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                problem = LeetCodeProblem(
                    href=row['href'],
                    question=row['question'],
                    completion_rate=row['completation_rate'],  # 注意拼写错误
                    level=row['level']
                )
                problems.append(problem)
        
        logger.info(f"加载完成: {len(problems)} 个问题")
        return problems
        
    except FileNotFoundError:
        logger.error(f"文件不存在: {csv_path}")
        return []
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"加载 CSV 失败: {error_message}")
        return []


class LeetCodeNotionProcessor:
    """LeetCode 到 Notion 的处理器"""
    
    def __init__(self, config: AppConfig):
        """初始化处理器"""
        self.config = config
        self.scraper = LeetCodeScraper(config.scraper_config)
        self.creator = LeetCodeNotionCreator(
            config.notion_config,
            progress_callback=self._progress_callback
        )
        self.stats = ProcessStats()
    
    def process_all(self, problems: List[LeetCodeProblem]):
        """
        处理所有问题
        
        Args:
            problems: 问题列表
        """
        self.stats.start_time = datetime.now()
        self.stats.total_problems = len(problems)
        
        # 限制处理数量
        if self.config.max_problems:
            problems = problems[:self.config.max_problems]
            logger.info(f"限制处理数量: {len(problems)}")
        
        logger.info(f"开始处理 {len(problems)} 个问题")
        logger.info("=" * 60)
        
        # 批量处理
        for i in range(0, len(problems), self.config.batch_size):
            batch = problems[i:i + self.config.batch_size]
            batch_num = i // self.config.batch_size + 1
            total_batches = (len(problems) + self.config.batch_size - 1) // self.config.batch_size
            
            logger.info(f"\n批次 {batch_num}/{total_batches}")
            logger.info("-" * 60)
            
            self._process_batch(batch, i)
        
        self.stats.end_time = datetime.now()
        self._print_summary()
    
    def _process_batch(self, batch: List[LeetCodeProblem], start_index: int):
        """处理一批问题"""
        for i, problem in enumerate(batch):
            current = start_index + i + 1
            self._process_single_problem(problem, current, self.stats.total_problems)
    
    def _process_single_problem(
        self,
        problem: LeetCodeProblem,
        current: int,
        total: int
    ):
        """
        处理单个问题
        
        Args:
            problem: 问题信息
            current: 当前索引
            total: 总数
        """
        logger.info(f"\n[{current}/{total}] {problem.problem_id} - {problem.problem_title}")
        
        try:
            # 1. 抓取详细信息
            detail = self.scraper.scrape_problem(problem)
            
            if detail.is_premium:
                self.stats.premium_problems += 1
                if self.config.skip_premium:
                    logger.info("跳过 Premium 问题")
                    return
            
            if detail.scrape_success:
                self.stats.scraped_success += 1
            else:
                self.stats.scraped_failed += 1
                logger.warning(f"抓取失败: {detail.scrape_error}")
            
            # 2. 创建 Notion 页面
            full_data = LeetCodeFullData(problem=problem, detail=detail)
            result = self.creator.create_problem_page(full_data)
            
            if result.success:
                self.stats.pages_created += 1
                self.stats.total_blocks += result.blocks_created
                logger.info(f"✓ 页面创建成功: {result.page_url}")
            else:
                self.stats.pages_failed += 1
                logger.error(f"✗ 页面创建失败: {result.error}")
        
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"处理失败: {error_message}")
            self.stats.pages_failed += 1
    
    def _progress_callback(self, message: str, current: int, total: int):
        """进度回调"""
        percentage = (current / total * 100) if total > 0 else 0
        logger.info(f"  [{percentage:.1f}%] {message}")
    
    def _print_summary(self):
        """打印处理摘要"""
        logger.info("\n" + "=" * 60)
        logger.info("处理完成!")
        logger.info("=" * 60)
        
        stats_dict = self.stats.to_dict()
        
        logger.info(f"总问题数: {stats_dict['total_problems']}")
        logger.info(f"抓取成功: {stats_dict['scraped_success']}")
        logger.info(f"抓取失败: {stats_dict['scraped_failed']}")
        logger.info(f"Premium 问题: {stats_dict['premium_problems']}")
        logger.info(f"页面创建成功: {stats_dict['pages_created']}")
        logger.info(f"页面创建失败: {stats_dict['pages_failed']}")
        logger.info(f"总 Blocks 数: {stats_dict['total_blocks']}")
        logger.info(f"总耗时: {stats_dict['duration_seconds']:.1f} 秒")
        logger.info(f"成功率: {stats_dict['success_rate']}")


def main():
    """主函数"""
    try:
        # 加载配置
        config = AppConfig.from_env()
        setup_logging(config)
        
        logger.info("LeetCode to Notion Converter")
        logger.info("=" * 60)
        
        # 加载问题
        problems = load_problems_from_csv(config.csv_path)
        
        if not problems:
            logger.error("没有找到问题，退出")
            return
        
        # 处理问题
        processor = LeetCodeNotionProcessor(config)
        processor.process_all(problems)
        
    except KeyboardInterrupt:
        logger.warning("\n用户中断")
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"程序失败: {error_message}")


if __name__ == "__main__":
    main()