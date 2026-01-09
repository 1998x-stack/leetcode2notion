"""
LeetCode 到 Notion 主程序
职责：协调整个流程 - CSV读取、网页抓取、Notion创建
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import os
import sys
import csv
import json
import traceback
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from loguru import logger
from dotenv import load_dotenv

from leetcode_models import LeetCodeProblem, Difficulty, ScrapingStats
from leetcode_scraper import LeetCodeScraperPlaywright
from leetcode_converter import LeetCodeNotionConverter
from leetcode_notion_creator import LeetCodeNotionCreator, NotionConfig


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level
    )
    
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation="10 MB"
        )


def load_problems_from_csv(csv_path: str) -> List[LeetCodeProblem]:
    """
    从 CSV 文件加载问题列表
    
    Args:
        csv_path: CSV 文件路径
        
    Returns:
        LeetCode 问题列表
    """
    problems = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # 提取问题编号
                question = row.get('question', '')
                parts = question.split('.', 1)
                
                if len(parts) < 2:
                    logger.warning(f"无法解析问题编号: {question}")
                    continue
                
                number = parts[0].strip()
                title = parts[1].strip()
                
                # 创建问题对象
                problem = LeetCodeProblem(
                    number=number,
                    title=title,
                    href=row.get('href', ''),
                    completion_rate=row.get('completation_rate', '0%'),
                    difficulty=Difficulty.from_string(row.get('level', 'Med.'))
                )
                
                problems.append(problem)
        
        logger.info(f"从 CSV 加载了 {len(problems)} 个问题")
        
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"加载 CSV 失败: {error_message}")
    
    return problems


def save_problems_to_json(problems: List[LeetCodeProblem], json_path: str):
    """
    保存问题数据到 JSON
    
    Args:
        problems: 问题列表
        json_path: JSON 文件路径
    """
    try:
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_problems": len(problems),
            "problems": [p.to_dict() for p in problems]
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"保存问题数据到: {json_path}")
        
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"保存 JSON 失败: {error_message}")


def load_problems_from_json(json_path: str) -> List[LeetCodeProblem]:
    """
    从 JSON 文件加载问题数据
    
    Args:
        json_path: JSON 文件路径
        
    Returns:
        问题列表
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        problems = []
        for p_dict in data.get('problems', []):
            problem = LeetCodeProblem(
                number=p_dict['number'],
                title=p_dict['title'],
                href=p_dict['href'],
                completion_rate=p_dict['completion_rate'],
                difficulty=Difficulty.from_string(p_dict['difficulty']),
                description=p_dict.get('description'),
                topics=p_dict.get('topics', []),
                hints=p_dict.get('hints', []),
                scrape_success=p_dict.get('scrape_success', False),
                error_message=p_dict.get('error_message'),
                requires_subscription=p_dict.get('requires_subscription', False),
            )
            problems.append(problem)
        
        logger.info(f"从 JSON 加载了 {len(problems)} 个问题")
        return problems
        
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"加载 JSON 失败: {error_message}")
        return []


def scrape_problems(
    problems: List[LeetCodeProblem],
    max_problems: Optional[int] = None,
    skip_subscription: bool = True
) -> ScrapingStats:
    """
    抓取问题详情
    
    Args:
        problems: 问题列表
        max_problems: 最大抓取数量
        skip_subscription: 是否跳过需要订阅的问题
        
    Returns:
        抓取统计信息
    """
    logger.info(f"开始抓取 {len(problems)} 个问题...")
    
    # 限制数量
    if max_problems:
        problems = problems[:max_problems]
    
    # scraper = LeetCodeScraperPlaywright(
    #     timeout=20,
    #     max_retries=2,
    # )
    
    stats = ScrapingStats(total_problems=len(problems))
    
    with LeetCodeScraperPlaywright(
        headless=True,
        block_resources=True,
        min_delay=2.0,
        max_delay=4.0
    ) as scraper:
        for problem in problems:
            success = scraper.scrape_problem(problem)
            
            if success:
                stats.successful_scrapes += 1
            elif problem.requires_subscription:
                stats.subscription_required += 1
                if skip_subscription:
                    logger.info(f"跳过订阅问题: {problem.display_title}")
            else:
                stats.failed_scrapes += 1
    
    logger.info(f"抓取完成: {stats.to_dict()}")
    
    return stats


def create_notion_pages(
    problems: List[LeetCodeProblem],
    notion_token: str,
    root_page_id: str,
    skip_failed_scrapes: bool = True
):
    """
    创建 Notion 页面
    
    Args:
        problems: 问题列表
        notion_token: Notion API token
        root_page_id: 根页面 ID
        skip_failed_scrapes: 是否跳过抓取失败的问题
    """
    logger.info(f"开始创建 {len(problems)} 个 Notion 页面...")
    
    config = NotionConfig(
        token=notion_token,
        root_page_id=root_page_id,
        rate_limit_delay=0.4,
        max_retries=3
    )
    
    creator = LeetCodeNotionCreator(config)
    
    results = creator.create_batch(problems, skip_failed_scrapes=skip_failed_scrapes)
    
    # 统计结果
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    logger.info(f"创建完成: {len(successful)} 成功, {len(failed)} 失败")
    
    # 显示失败的问题
    if failed:
        logger.warning("失败的问题:")
        for r in failed[:10]:  # 只显示前10个
            logger.warning(f"  - {r.problem_title}: {r.error}")


def main():
    """主函数"""
    setup_logging(level="INFO", log_file="leetcode_to_notion.log")
    
    logger.info("=" * 60)
    logger.info("LeetCode 到 Notion 转换工具")
    logger.info("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    notion_token = os.getenv("NOTION_TOKEN")
    root_page_id = os.getenv("NOTION_ROOT_PAGE_ID")
    
    if not notion_token or not root_page_id:
        logger.error("请设置 NOTION_TOKEN 和 NOTION_ROOT_PAGE_ID 环境变量")
        return
    
    # 配置参数
    csv_path = "leetcode.csv"
    json_cache_path = "leetcode_problems.json"
    
    # 是否使用缓存
    use_cache = False
    if Path(json_cache_path).exists():
        response = input(f"发现缓存文件 {json_cache_path}，是否使用? (y/n): ")
        use_cache = response.lower() == 'y'
    
    # 1. 加载问题
    if use_cache:
        problems = load_problems_from_json(json_cache_path)
    else:
        problems = load_problems_from_csv(csv_path)
    
    if not problems:
        logger.error("没有加载到问题数据")
        return
    
    # 2. 抓取问题详情（如果需要）
    if not use_cache:
        # 询问要抓取多少个
        max_problems = None
        response = input(f"要抓取多少个问题? (回车抓取全部 {len(problems)} 个): ")
        if response.strip():
            try:
                max_problems = int(response)
            except ValueError:
                logger.warning("无效输入，将抓取全部")
        
        stats = scrape_problems(
            problems,
            max_problems=max_problems,
            skip_subscription=True
        )
        
        # 保存到 JSON
        save_problems_to_json(problems, json_cache_path)
        
        logger.info(f"抓取统计: {stats.to_dict()}")
    
    # 3. 创建 Notion 页面
    # 只创建成功抓取的问题
    problems_to_create = [p for p in problems if p.scrape_success]
    
    logger.info(f"准备创建 {len(problems_to_create)} 个问题页面")
    
    if not problems_to_create:
        logger.warning("没有成功抓取的问题可以创建")
        return
    
    # response = input(f"是否开始创建 {len(problems_to_create)} 个 Notion 页面? (y/n): ")
    # if response.lower() != 'y':
    #     logger.info("取消创建")
    #     return
    
    create_notion_pages(
        problems_to_create,
        notion_token,
        root_page_id,
        skip_failed_scrapes=True
    )
    
    logger.info("=" * 60)
    logger.info("处理完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()