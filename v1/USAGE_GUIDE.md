# LeetCode to Notion - Complete Usage Guide

## 🎯 目标
将 LeetCode 题目批量转换为美观的 Notion 页面，包含题目描述、提示、代码模板等完整内容。

## 📦 第一步：安装和配置

### 1.1 创建项目目录
```bash
mkdir leetcode-to-notion
cd leetcode-to-notion
```

### 1.2 创建虚拟环境（推荐）
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 1.3 安装依赖
创建所有 Python 文件后，运行：
```bash
pip install -r requirements.txt
```

### 1.4 配置 Notion Integration

#### Step 1: 创建 Integration
1. 访问 https://www.notion.so/my-integrations
2. 点击 "+ New integration"
3. 填写信息：
   - Name: `LeetCode Importer`
   - Associated workspace: 选择你的工作空间
   - Type: `Internal integration`
4. 点击 "Submit"
5. **复制 Internal Integration Token**（以 `secret_` 开头）

#### Step 2: 获取 Root Page ID
1. 在 Notion 中创建一个新页面（例如：`LeetCode Problems`）
2. 点击右上角 "Share" → "Copy link"
3. 链接格式：`https://www.notion.so/My-Page-xxxxx?v=yyyyy`
4. `xxxxx` 就是 Page ID（32 位字符）

#### Step 3: 连接 Integration 到页面
**重要步骤！！！**
1. 打开你的 Notion 页面
2. 点击右上角 "•••" 菜单
3. 向下滚动找到 "Connections"
4. 点击 "Add connections"
5. 选择你刚创建的 Integration（`LeetCode Importer`）

### 1.5 创建 .env 文件
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用任何文本编辑器
```

填入你的信息：
```env
NOTION_TOKEN=secret_your_token_here
NOTION_ROOT_PAGE_ID=your_page_id_here
```

## 🧪 第二步：测试环境

运行测试脚本验证配置：
```bash
python test_setup.py
```

期望输出：
```
============================================================
LeetCode to Notion - 环境测试
============================================================
检查依赖包...
  ✓ notion_client
  ✓ requests
  ✓ bs4
  ✓ loguru
  ✓ dotenv

检查环境变量...
  ✓ NOTION_TOKEN: secret_xxxxx...
  ✓ NOTION_ROOT_PAGE_ID: abc123...

测试 Notion API 连接...
  ✓ 成功连接到页面: {'title': [{'text': {'content': 'LeetCode Problems'}}]}

检查 CSV 文件...
  ✓ leetcode.csv 包含 100 行数据
  ✓ CSV 格式正确
  示例数据:
    1. Two Sum
    难度: Easy
    完成率: 56.8%

============================================================
✅ 所有测试通过！可以运行 main.py
============================================================
```

如果有错误，请根据提示修复。

## 🚀 第三步：运行程序

### 3.1 首次运行（小批量测试）
建议先测试 5 个题目：
```bash
python main.py
```

交互过程：
```
====================================================
LeetCode 到 Notion 转换工具
====================================================
从 CSV 加载了 100 个问题
要抓取多少个问题? (回车抓取全部 100 个): 5
开始抓取 5 个问题...
[20.0%] 抓取 1. Two Sum
[40.0%] 抓取 2. Add Two Numbers
[60.0%] 抓取 3. Longest Substring Without Repeating Characters
[80.0%] 抓取 4. Median of Two Sorted Arrays
[100.0%] 抓取 5. Longest Palindromic Substring
抓取完成: {
  "successful_scrapes": 4,
  "failed_scrapes": 0,
  "subscription_required": 1,
  "success_rate": "80.0%"
}
保存问题数据到: leetcode_problems.json
准备创建 4 个问题页面
是否开始创建 4 个 Notion 页面? (y/n): y
[25.0%] 创建 1. Two Sum
[50.0%] 创建 2. Add Two Numbers
[75.0%] 创建 3. Longest Substring Without Repeating Characters
[100.0%] 创建 5. Longest Palindromic Substring
创建完成: 4 成功, 0 失败
====================================================
处理完成！
====================================================
```

### 3.2 检查结果
1. 打开你的 Notion 页面
2. 应该看到 4 个子页面，每个对应一道 LeetCode 题目
3. 点开任意一个，查看内容是否完整

### 3.3 批量运行
如果测试成功，可以抓取更多题目：
```bash
python main.py
```

这次选择使用缓存：
```
发现缓存文件 leetcode_problems.json，是否使用? (y/n): n
要抓取多少个问题? (回车抓取全部 100 个): 50
```

## 📊 第四步：查看结果

### 4.1 Notion 页面结构
每个题目页面包含：

```
┌─────────────────────────────────────┐
│ 🟢 1. Two Sum                        │
├─────────────────────────────────────┤
│ 📊 Callout: 难度、完成率            │
├─────────────────────────────────────┤
│ 📝 Problem Description              │
│    [Callout with description]       │
├─────────────────────────────────────┤
│ 💻 Solution                         │
│    [Python code template]           │
│    🌐 More Language Templates       │
│       [JavaScript, Java]            │
├─────────────────────────────────────┤
│ 💡 Hints (if available)             │
│    [Quote blocks for each hint]     │
├─────────────────────────────────────┤
│ 🔗 Similar Questions (if available) │
│    [Callout with links]             │
├─────────────────────────────────────┤
│ 🏷️ Topics                           │
│    • Array                          │
│    • Hash Table                     │
├─────────────────────────────────────┤
│ 📚 Resources                        │
│    [Bookmark to LeetCode]           │
│    [Links to Solutions & Discuss]   │
└─────────────────────────────────────┘
```

### 4.2 代码模板示例
每个题目包含多语言代码模板：

**Python:**
```python
# 1. Two Sum
# Difficulty: Easy
# Acceptance: 56.8%

class Solution:
    def solve(self):
        # Write your solution here
        pass

# Test cases
if __name__ == "__main__":
    solution = Solution()
    # Add your test cases here
    pass
```

**JavaScript:**
```javascript
// 1. Two Sum
// Difficulty: Easy

var solve = function() {
    // Write your solution here
};
```

### 4.3 查看日志
所有日志保存在 `leetcode_to_notion.log`：
```bash
cat leetcode_to_notion.log

# 或实时查看
tail -f leetcode_to_notion.log
```

## 🔧 高级用法

### 方案 1：分批处理
如果题目很多，可以分批运行：

```python
# 修改 main.py 中的代码
problems_to_create = problems[:10]  # 只创建前 10 个
```

### 方案 2：只创建特定难度
```python
# 只创建 Easy 题目
problems_to_create = [p for p in problems if p.difficulty == Difficulty.EASY and p.scrape_success]
```

### 方案 3：跳过已创建的题目
手动维护一个已创建列表：
```python
created_numbers = {'1', '2', '3'}  # 已创建的题目编号
problems_to_create = [p for p in problems if p.number not in created_numbers and p.scrape_success]
```

### 方案 4：自定义选择器
如果 LeetCode 页面结构变化，更新选择器：

```python
# 在 leetcode_scraper.py 中
def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
    selectors = [
        '.gap-1+ div .elfjS',          # 当前选择器
        '[data-track-load="description"]',  # 备用选择器
        '.question-content',           # 旧版选择器
        # 添加新的选择器
    ]
```

## ⚠️ 常见问题排查

### Q1: `validation_error` from Notion API
**问题：** Notion API 返回验证错误

**解决方案：**
1. 检查 block 文本长度是否超过 2000 字符
2. 查看日志中的具体错误信息
3. 尝试减少 `MAX_TEXT_LENGTH` 设置

### Q2: 抓取失败率高
**问题：** 很多题目抓取失败

**解决方案：**
```python
# 增加超时时间和重试次数
scraper = LeetCodeScraper(
    timeout=30,        # 从 15 增加到 30
    max_retries=5,     # 从 3 增加到 5
    rate_limit_delay=2.0  # 从 1.5 增加到 2.0
)
```

### Q3: "requires subscription" 太多
**问题：** 很多题目需要订阅

**解决方案：**
- 这是正常的，LeetCode 有很多 Premium 题目
- 程序会自动跳过这些题目
- 只处理免费题目即可

### Q4: 找不到题目描述
**问题：** 页面显示但描述为空

**解决方案：**
1. 手动访问该题目的 LeetCode 页面
2. 右键 → 检查元素
3. 找到描述部分的 CSS 选择器
4. 更新 `_extract_description` 方法

### Q5: Notion 页面乱码
**问题：** 中文显示异常

**解决方案：**
```python
# 确保 CSV 使用 UTF-8 编码
with open(csv_path, 'r', encoding='utf-8') as f:
    # ...
```

## 📈 性能优化

### 并发抓取（高级）
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def scrape_concurrent(problems, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, scraper.scrape_problem, p)
            for p in problems
        ]
        await asyncio.gather(*tasks)
```

### 使用代理（如果被限制）
```python
scraper = LeetCodeScraper(
    timeout=15,
    max_retries=3,
    rate_limit_delay=1.5,
)
scraper.session.proxies = {
    'http': 'http://your-proxy:port',
    'https': 'https://your-proxy:port',
}
```

## 🎓 学习建议

### 使用 Notion 页面学习
1. **每日一题**：在 Notion 中添加 "Status" 属性（Not Started/In Progress/Completed）
2. **添加笔记**：在代码下方添加你的解题思路
3. **时间追踪**：使用 Notion 的日期属性记录完成时间
4. **标签分类**：按主题（数组、动态规划等）创建数据库视图

### 扩展功能建议
1. **添加难度过滤**：在 Notion 中创建筛选视图
2. **进度追踪**：使用 Notion 公式计算完成百分比
3. **复习计划**：使用 Notion 的 Reminder 功能
4. **笔记模板**：为每个题目添加固定的笔记结构

## 🔄 更新和维护

### 定期更新题库
```bash
# 下载最新的 leetcode.csv
# 运行程序更新新题目
python main.py
```

### 清理缓存
```bash
# 删除缓存文件，重新抓取
rm leetcode_problems.json
python main.py
```

### 备份 Notion 数据
使用 Notion 的导出功能定期备份：
1. 页面右上角 "•••"
2. "Export"
3. 选择 "Markdown & CSV"

## 🎉 完成！

现在你已经拥有了一个完整的 LeetCode 学习库！

祝你刷题愉快！💪