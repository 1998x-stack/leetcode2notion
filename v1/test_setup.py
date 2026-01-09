"""
测试脚本 - 验证环境配置
职责：检查依赖、环境变量和 Notion API 连接
"""
import os
import sys
from dotenv import load_dotenv
from loguru import logger

def check_dependencies():
    """检查依赖包"""
    logger.info("检查依赖包...")
    
    required_packages = [
        'notion_client',
        'requests',
        'bs4',
        'loguru',
        'dotenv',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"  ✓ {package}")
        except ImportError:
            missing.append(package)
            logger.error(f"  ✗ {package}")
    
    if missing:
        logger.error(f"缺少依赖: {', '.join(missing)}")
        logger.error("请运行: pip install -r requirements.txt")
        return False
    
    return True


def check_env_variables():
    """检查环境变量"""
    logger.info("检查环境变量...")
    
    load_dotenv()
    
    notion_token = os.getenv("NOTION_TOKEN")
    root_page_id = os.getenv("NOTION_ROOT_PAGE_ID")
    
    if not notion_token:
        logger.error("  ✗ NOTION_TOKEN 未设置")
        logger.error("请在 .env 文件中设置 NOTION_TOKEN")
        return False
    
    logger.info(f"  ✓ NOTION_TOKEN: {notion_token[:20]}...")
    
    if not root_page_id:
        logger.error("  ✗ NOTION_ROOT_PAGE_ID 未设置")
        logger.error("请在 .env 文件中设置 NOTION_ROOT_PAGE_ID")
        return False
    
    logger.info(f"  ✓ NOTION_ROOT_PAGE_ID: {root_page_id}")
    
    return True


def test_notion_connection():
    """测试 Notion API 连接"""
    logger.info("测试 Notion API 连接...")
    
    try:
        from notion_client import Client
        
        notion_token = os.getenv("NOTION_TOKEN")
        client = Client(auth=notion_token)
        
        # 测试 API 调用
        root_page_id = os.getenv("NOTION_ROOT_PAGE_ID")
        
        try:
            page = client.pages.retrieve(page_id=root_page_id)
            logger.info(f"  ✓ 成功连接到页面: {page.get('properties', {}).get('title', {})}")
            return True
        except Exception as e:
            logger.error(f"  ✗ 无法访问页面: {e}")
            logger.error("请检查:")
            logger.error("  1. Page ID 是否正确")
            logger.error("  2. Integration 是否已添加到该页面的 Connections")
            return False
            
    except Exception as e:
        logger.error(f"  ✗ Notion API 连接失败: {e}")
        return False


def check_csv_file():
    """检查 CSV 文件"""
    logger.info("检查 CSV 文件...")
    
    csv_path = "leetcode.csv"
    
    if not os.path.exists(csv_path):
        logger.warning(f"  ⚠ {csv_path} 不存在")
        logger.warning("请确保 leetcode.csv 文件在当前目录")
        return False
    
    try:
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                logger.error(f"  ✗ {csv_path} 为空")
                return False
            
            logger.info(f"  ✓ {csv_path} 包含 {len(rows)} 行数据")
            
            # 检查必需的列
            required_columns = ['href', 'question', 'completation_rate', 'level']
            first_row = rows[0]
            
            for col in required_columns:
                if col not in first_row:
                    logger.error(f"  ✗ 缺少列: {col}")
                    return False
            
            logger.info(f"  ✓ CSV 格式正确")
            
            # 显示示例
            logger.info("  示例数据:")
            logger.info(f"    {first_row.get('question')}")
            logger.info(f"    难度: {first_row.get('level')}")
            logger.info(f"    完成率: {first_row.get('completation_rate')}")
            
            return True
            
    except Exception as e:
        logger.error(f"  ✗ 读取 CSV 失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    logger.info("=" * 60)
    logger.info("LeetCode to Notion - 环境测试")
    logger.info("=" * 60)
    
    all_passed = True
    
    # 1. 检查依赖
    if not check_dependencies():
        all_passed = False
    
    logger.info("")
    
    # 2. 检查环境变量
    if not check_env_variables():
        all_passed = False
    
    logger.info("")
    
    # 3. 测试 Notion 连接
    if not test_notion_connection():
        all_passed = False
    
    logger.info("")
    
    # 4. 检查 CSV 文件
    if not check_csv_file():
        all_passed = False
    
    logger.info("")
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("✅ 所有测试通过！可以运行 main.py")
    else:
        logger.error("❌ 部分测试失败，请先解决上述问题")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()