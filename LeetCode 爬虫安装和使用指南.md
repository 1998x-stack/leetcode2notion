# LeetCode 爬虫安装和使用指南

## 📦 安装依赖

### 1. 安装 Playwright

```bash
# 安装 Python 库
pip install playwright loguru

# 安装浏览器驱动（必需！）
playwright install chromium
```

### 2. 依赖说明

```txt
playwright>=1.40.0
loguru>=0.7.0
```

## 🚀 快速开始

### 基础使用

```python
from leetcode_scraper_playwright import LeetCodeScraperPlaywright
from leetcode_models import LeetCodeProblem, Difficulty

# 创建问题对象
problem = LeetCodeProblem(
    display_title="1. Two Sum",
    href="https://leetcode.com/problems/two-sum/",
    difficulty=Difficulty.EASY,
    problem_number=1
)

# 使用上下文管理器（推荐）
with LeetCodeScraperPlaywright(headless=True) as scraper:
    success = scraper.scrape_problem(problem)
    
    if success:
        print(f"描述: {problem.description[:100]}...")
        print(f"主题: {problem.topics}")
        print(f"提示数: {len(problem.hints)}")
```

### 批量抓取

```python
problems = [
    LeetCodeProblem(
        display_title="1. Two Sum",
        href="https://leetcode.com/problems/two-sum/",
        difficulty=Difficulty.EASY,
        problem_number=1
    ),
    LeetCodeProblem(
        display_title="2. Add Two Numbers",
        href="https://leetcode.com/problems/add-two-numbers/",
        difficulty=Difficulty.MEDIUM,
        problem_number=2
    ),
    # ... 更多问题
]

with LeetCodeScraperPlaywright(
    headless=True,
    min_delay=3.0,
    max_delay=6.0
) as scraper:
    successful = scraper.scrape_batch(problems)
    print(f"成功抓取: {successful}/{len(problems)}")
```

## ⚙️ 配置选项

### 初始化参数

```python
scraper = LeetCodeScraperPlaywright(
    timeout=30000,           # 页面超时（毫秒）
    max_retries=3,          # 最大重试次数
    min_delay=2.0,          # 最小延迟（秒）
    max_delay=5.0,          # 最大延迟（秒）
    headless=True,          # 无头模式
    block_resources=True,   # 阻止图片/字体等资源
    progress_callback=None  # 自定义进度回调
)
```

### 推荐配置

#### 🏃 快速模式（测试用）
```python
scraper = LeetCodeScraperPlaywright(
    headless=True,
    min_delay=1.0,
    max_delay=2.0,
    block_resources=True
)
```

#### 🛡️ 安全模式（推荐）
```python
scraper = LeetCodeScraperPlaywright(
    headless=True,
    min_delay=3.0,
    max_delay=6.0,
    block_resources=True,
    max_retries=5
)
```

#### 🐌 保守模式（避免封禁）
```python
scraper = LeetCodeScraperPlaywright(
    headless=True,
    min_delay=5.0,
    max_delay=10.0,
    block_resources=True,
    max_retries=3
)
```

## 🔧 高级功能

### 自定义进度回调

```python
def my_progress(message: str, current: int, total: int):
    percentage = (current / total * 100)
    print(f"[{percentage:.1f}%] {message}")
    # 可以更新UI、写入日志等

with LeetCodeScraperPlaywright(
    progress_callback=my_progress
) as scraper:
    scraper.scrape_batch(problems)
```

### 调试模式

```python
# 显示浏览器窗口（方便调试）
with LeetCodeScraperPlaywright(
    headless=False,  # 显示浏览器
    block_resources=False  # 加载所有资源
) as scraper:
    scraper.scrape_problem(problem)
```

### 错误处理

```python
with LeetCodeScraperPlaywright() as scraper:
    for problem in problems:
        success = scraper.scrape_problem(problem)
        
        if not success:
            if problem.requires_subscription:
                print(f"需要订阅: {problem.display_title}")
            elif problem.error_message:
                print(f"错误: {problem.error_message}")
```

## 📊 性能优化建议

### 1. 资源阻止
```python
# 阻止不必要资源，提升速度
block_resources=True  # 推荐开启
```

### 2. 延迟设置
```python
# 平衡速度和安全
min_delay=3.0  # 不建议低于2秒
max_delay=6.0  # 添加随机性
```

### 3. 批量处理
```python
# 一次会话处理多个问题，复用浏览器实例
with LeetCodeScraperPlaywright() as scraper:
    scraper.scrape_batch(problems)  # 比逐个创建scraper快
```

### 4. 并发控制
```python
# 如需并发，使用多个 scraper 实例
from concurrent.futures import ThreadPoolExecutor

def scrape_with_instance(problem_batch):
    with LeetCodeScraperPlaywright() as scraper:
        return scraper.scrape_batch(problem_batch)

# 分批处理
batch_size = 50
batches = [problems[i:i+batch_size] for i in range(0, len(problems), batch_size)]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(scrape_with_instance, batches))
```

## 🚨 常见问题

### Q1: 仍然收到 403 错误？

**解决方案：**
1. 增加延迟时间
```python
min_delay=5.0, max_delay=10.0
```

2. 减少重试次数（避免被识别为攻击）
```python
max_retries=2
```

3. 检查 User-Agent 是否最新

### Q2: 页面超时？

**解决方案：**
```python
timeout=60000  # 增加到60秒
```

### Q3: 内存占用过高？

**解决方案：**
1. 开启资源阻止
```python
block_resources=True
```

2. 分批处理，定期重启
```python
batch_size = 100
for batch in batches:
    with LeetCodeScraperPlaywright() as scraper:
        scraper.scrape_batch(batch)
    # 浏览器会在 with 结束时自动关闭
```

### Q4: 无法提取某些信息？

**原因：** LeetCode 可能更新了页面结构

**解决方案：**
1. 使用无头模式调试
```python
headless=False
```

2. 查看页面结构，更新选择器

### Q5: Playwright 安装失败？

```bash
# 如果网络问题，使用镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://playwright.azureedge.net
playwright install chromium

# 或使用国内镜像
pip install playwright -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## ⚠️ 注意事项

### 法律合规
1. ✅ 仅用于个人学习和研究
2. ✅ 遵守 robots.txt
3. ✅ 控制请求频率
4. ❌ 不要转售或商业使用数据
5. ❌ 不要给 LeetCode 服务器造成过大压力

### 使用建议
1. **延迟设置**: 建议 3-6 秒随机延迟
2. **批量限制**: 单次不超过 100-200 题
3. **时间分散**: 避免短时间大量请求
4. **Premium 内容**: 无法通过爬虫获取，尊重付费内容

## 📈 性能对比

| 方法 | 速度 | 成功率 | 资源占用 |
|------|------|--------|----------|
| Requests | 快 | ~0% (403) | 低 |
| Selenium | 中 | ~60% | 高 |
| **Playwright** | 中-快 | **~90%** | 中 |

## 🔄 从旧版本迁移

### 替换 requests
```python
# 旧代码（requests）
from leetcode_scraper import LeetCodeScraper
scraper = LeetCodeScraper()

# 新代码（Playwright）
from leetcode_scraper_playwright import LeetCodeScraperPlaywright
with LeetCodeScraperPlaywright() as scraper:
    # 使用方式相同
    scraper.scrape_problem(problem)
```

### API 兼容性
新版本保持了与旧版本相同的接口：
- ✅ `scrape_problem(problem)` 
- ✅ `scrape_batch(problems)`
- ✅ 相同的返回值和错误处理

## 📚 相关资源

- [Playwright 官方文档](https://playwright.dev/python/)
- [LeetCode 服务条款](https://leetcode.com/terms/)
- [反爬虫最佳实践](https://scrapfly.io/blog/web-scraping-best-practices/)

## 💡 最佳实践示例

```python
import sys
from loguru import logger
from leetcode_scraper_playwright import LeetCodeScraperPlaywright
from leetcode_models import LeetCodeProblem

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("leetcode_scraper.log", rotation="10 MB", level="DEBUG")

# 加载问题列表
problems = load_problems_from_csv("problems.csv")

# 批量抓取，自动处理失败和重试
with LeetCodeScraperPlaywright(
    headless=True,
    min_delay=3.0,
    max_delay=6.0,
    block_resources=True,
    max_retries=3
) as scraper:
    successful = scraper.scrape_batch(
        problems,
        skip_subscription=True  # 跳过付费题目
    )

print(f"抓取完成: {successful}/{len(problems)}")

# 保存结果
save_problems_to_csv(problems, "results.csv")
```