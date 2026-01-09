"""
配置测试脚本
用于验证 Notion 配置和创建测试页面
"""
import sys
import traceback
from datetime import datetime
from loguru import logger

from config import AppConfig
from models import LeetCodeProblem, LeetCodeDetail, LeetCodeFullData
from notion_creator import LeetCodeNotionCreator


def setup_logging():
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )


def test_notion_connection():
    """测试 Notion 连接"""
    logger.info("=" * 60)
    logger.info("测试 Notion 配置")
    logger.info("=" * 60)
    
    try:
        # 加载配置
        config = AppConfig.from_env()
        logger.info(f"✓ 配置加载成功")
        logger.info(f"  Root Page ID: {config.notion_config.root_page_id}")
        
        # 创建测试页面
        creator = LeetCodeNotionCreator(config.notion_config)
        
        # 创建测试数据
        test_problem = LeetCodeProblem(
            href="https://leetcode.com/problems/two-sum",
            question="1. Two Sum",
            completion_rate="56.8%",
            level="Easy"
        )
        
        test_detail = LeetCodeDetail(
            description="""Given an array of integers nums and an integer target, 
return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, 
and you may not use the same element twice.

You can return the answer in any order.""",
            topics=["Array", "Hash Table"],
            hints=[
                "A really brute force way would be to search for all possible pairs of numbers but that would be too slow.",
                "Try using a hash table to improve the time complexity."
            ],
            similar_questions=[
                "3Sum",
                "4Sum",
                "Two Sum II - Input Array Is Sorted"
            ],
            scrape_success=True
        )
        
        test_data = LeetCodeFullData(
            problem=test_problem,
            detail=test_detail
        )
        
        logger.info("创建测试页面...")
        result = creator.create_problem_page(test_data)
        
        if result.success:
            logger.info("=" * 60)
            logger.info("✓ 测试成功!")
            logger.info("=" * 60)
            logger.info(f"页面 ID: {result.page_id}")
            logger.info(f"页面 URL: {result.page_url}")
            logger.info(f"Blocks 数量: {result.blocks_created}")
            logger.info("")
            logger.info("请在 Notion 中查看测试页面")
            logger.info("如果一切正常，可以运行 main.py 开始批量处理")
        else:
            logger.error("=" * 60)
            logger.error("✗ 测试失败")
            logger.error("=" * 60)
            logger.error(f"错误: {result.error}")
            logger.error("")
            logger.error("请检查：")
            logger.error("1. NOTION_TOKEN 是否正确")
            logger.error("2. NOTION_ROOT_PAGE_ID 是否正确")
            logger.error("3. Integration 是否已添加到页面")
        
    except ValueError as e:
        logger.error("=" * 60)
        logger.error("✗ 配置错误")
        logger.error("=" * 60)
        logger.error(f"错误: {str(e)}")
        logger.error("")
        logger.error("请检查 .env 文件是否存在并正确配置")
        
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error("=" * 60)
        logger.error("✗ 未知错误")
        logger.error("=" * 60)
        logger.error(f"错误: {error_message}")


if __name__ == "__main__":
    setup_logging()
    test_notion_connection()