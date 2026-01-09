# LeetCode to Notion Converter

将 LeetCode 题目自动转换为美观的 Notion 页面，支持题目描述、提示、相似问题、代码模板等丰富内容。

## ✨ 特性

- 📊 **从 CSV 批量导入** - 支持从 leetcode.csv 批量读取题目
- 🔍 **智能网页抓取** - 自动提取题目描述、主题标签、提示、相似问题
- 🎨 **美观的 Notion 页面** - 使用 Callout、Quote、Code 等丰富元素
- 🔄 **缓存机制** - 支持 JSON 缓存，避免重复抓取
- ⚡ **速率限制处理** - 自动处理 API 速率限制和重试
- 🎯 **CleanRL 设计** - 单一职责、显式依赖、易于测试

## 📋 页面内容

每个 LeetCode 问题页面包含：

### 📌 头部信息
- **难度标识** (🟢 Easy / 🟡 Medium / 🔴 Hard)
- **完成率**
- **问题编号**

### 📝 问题描述
- 使用 Callout 展示完整题目描述
- 自动处理长文本分段

### 💻 解题代码区
- **Python 代码模板** - 预设类和测试用例
- **多语言支持** - 可折叠的 JavaScript、Java 模板

### 💡 提示部分
- 每个提示使用 Quote block 展示
- 黄色背景高亮

### 🔗 相似问题
- Callout 列表展示
- 每个问题带链接

### 🏷️ 主题标签
- Bullet list 显示所有标签
- 代码样式格式

### 📚 资源链接
- LeetCode 原题链接（Bookmark）
- Solutions 和 Discuss 链接

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
NOTION_TOKEN=your_notion_integration_token
NOTION_ROOT_PAGE_ID=your_root_page_id
```

**获取 Notion Token：**
1. 访问 https://www.notion.so/my-integrations
2. 创建新的 Integration
3. 复制 Internal Integration Token

**获取 Root Page ID：**
1. 打开 Notion 页面
2. 点击右上角 "Share" → "Copy link"
3. 链接格式：`https://notion.so/xxxxx-yyyyy`
4. `xxxxx` 或 `yyyyy` 就是 Page ID

**重要：** 需要在 Notion 页面设置中，将你的 Integration 添加到该页面的 Connections 中！

### 3. 准备 CSV 文件

确保 `leetcode.csv` 文件格式正确：

```csv
"href","question","completation_rate","level"
"https://leetcode.com/problems/two-sum","1. Two Sum","56.8%","Easy"
"https://leetcode.com/problems/add-two-numbers","2. Add Two Numbers","47.6%","Med."
```

### 4. 运行程序

```bash
python main.py
```

## 📖 使用流程

程序会按以下步骤执行：

### Step 1: 加载题目
```
从 CSV 加载了 XX 个问题
```

### Step 2: 抓取详情
```
要抓取多少个问题? (回车抓取全部): 10
开始抓取 10 个问题...
[10.0%] 抓取 1. Two Sum
...
抓取完成: {'successful_scrapes': 8, 'failed_scrapes': 2, ...}
```

### Step 3: 创建 Notion 页面
```
准备创建 8 个问题页面
是否开始创建 8 个 Notion 页面? (y/n): y
[12.5%] 创建 1. Two Sum
...
创建完成: 8 成功, 0 失败
```

## 🏗️ 项目结构

```
leetcode-to-notion/
├── leetcode_models.py          # 数据模型定义
├── leetcode_scraper.py         # 网页抓取器
├── leetcode_converter.py       # Notion 转换器
├── leetcode_notion_creator.py  # Notion 页面创建器
├── main.py                     # 主程序
├── requirements.txt            # 依赖清单
├── .env                        # 环境变量（需创建）
├── leetcode.csv               # 输入 CSV（需提供）
└── leetcode_problems.json     # 缓存文件（自动生成）
```

## 🔧 核心模块

### LeetCodeProblem (Data Model)
```python
@dataclass
class LeetCodeProblem:
    number: str
    title: str
    href: str
    difficulty: Difficulty
    description: Optional[str]
    topics: List[str]
    hints: List[str]
    similar_questions: List[SimilarQuestion]
```

### LeetCodeScraper
```python
scraper = LeetCodeScraper(
    timeout=15,
    max_retries=3,
    rate_limit_delay=1.5
)
scraper.scrape_problem(problem)
```

### LeetCodeNotionConverter
```python
converter = LeetCodeNotionConverter()
blocks = converter.convert_problem(problem)
```

### LeetCodeNotionCreator
```python
creator = LeetCodeNotionCreator(config)
result = creator.create_problem_page(problem)
```

## ⚠️ 注意事项

### 订阅限制
某些 LeetCode 题目需要 Premium 订阅才能访问。程序会：
- 自动检测需要订阅的题目
- 标记为 `requires_subscription = True`
- 默认跳过这些题目

### 速率限制
- **LeetCode**: 请求间隔 1.5 秒
- **Notion API**: 请求间隔 0.4 秒
- 自动重试机制，指数退避

### 错误处理
所有异常都使用 loguru 记录：
```python
exc_type, exc_value, exc_traceback = sys.exc_info()
error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
logger.error(error_message)
```

## 🎯 使用建议

### 1. 小批量测试
首次运行建议先测试 5-10 个题目：
```
要抓取多少个问题? 5
```

### 2. 使用缓存
抓取完成后，数据会保存到 `leetcode_problems.json`。下次运行时可以直接使用缓存：
```
发现缓存文件，是否使用? (y/n): y
```

### 3. 分批创建
如果题目很多，可以修改 `main.py` 中的 `problems_to_create` 列表，分批创建。

### 4. 查看日志
所有日志保存在 `leetcode_to_notion.log`：
```bash
tail -f leetcode_to_notion.log
```

## 🐛 常见问题

### Q: 抓取失败率很高？
A: 可能的原因：
- 网络问题，增加 timeout
- LeetCode 网页结构变化，更新 CSS 选择器
- 被反爬虫，增加 rate_limit_delay

### Q: Notion API 报错 "validation_error"？
A: 检查：
- Block 结构是否正确
- 文本长度是否超过 2000 字符
- Rich text 格式是否有误

### Q: 找不到题目描述？
A: LeetCode 页面结构可能变化，更新 `_extract_description` 中的选择器。

## 📊 示例输出

```
====================================================
LeetCode 到 Notion 转换工具
====================================================
从 CSV 加载了 100 个问题
开始抓取 10 个问题...
[100.0%] 抓取 10. Palindrome Number
抓取完成: {
  "successful_scrapes": 8,
  "failed_scrapes": 0,
  "subscription_required": 2,
  "success_rate": "80.0%"
}
准备创建 8 个问题页面
是否开始创建 8 个 Notion 页面? (y/n): y
[100.0%] 创建 9. Palindrome Number
创建完成: 8 成功, 0 失败
====================================================
处理完成！
====================================================
```

## 📝 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

遵循 CleanRL 设计原则：
- 单一职责 - 每个模块只做一件事
- 显式依赖 - 所有依赖通过参数传递
- 易于测试 - 纯函数和清晰的接口

## 🙏 致谢

- [Notion API](https://developers.notion.com/)
- [LeetCode](https://leetcode.com/)
- [CleanRL](https://github.com/vwxyzjn/cleanrl) - 设计灵感