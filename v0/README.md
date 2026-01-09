# LeetCode to Notion Converter

自动将 LeetCode 问题转换为精美的 Notion 页面，包含题目描述、代码模板、提示等。

## ✨ 特性

- 📝 **完整的题目信息**：难度、完成率、题目描述、主题标签
- 💻 **代码模板**：自动生成 Python 代码模板
- 💡 **智能提示**：以 Quote 块展示所有提示
- 🔗 **相似问题**：Callout 块显示相关问题
- 📊 **进度追踪**：实时显示处理进度和统计
- 🎨 **精美排版**：充分利用 Notion 各种 block 类型

## 📋 页面结构

每个 LeetCode 问题页面包含：

1. **问题信息头部** (Callout)
   - 难度级别（带图标 🟢🟡🔴）
   - 完成率
   - 问题 ID

2. **LeetCode 链接** (Bookmark)

3. **问题描述** (Callout - 蓝色背景)

4. **主题标签** (粗体段落)

5. **解决方案区域** (Code Block)
   - Python 代码模板
   - 时间复杂度分析

6. **提示** (Quote Blocks)
   - 每个提示单独一个 Quote

7. **相似问题** (Callout - 灰色背景)

8. **笔记区域** (段落)

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Notion

1. 创建 Notion Integration：
   - 访问 https://www.notion.so/my-integrations
   - 点击 "+ New integration"
   - 复制 "Internal Integration Token"

2. 准备 Notion 页面：
   - 在 Notion 中创建一个空白页面
   - 点击右上角 "Share"
   - 点击 "Invite" 并添加你的 Integration
   - 复制页面 ID（URL 中的部分）

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
NOTION_TOKEN=secret_xxxxxxxxxxxxx
NOTION_ROOT_PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LEETCODE_CSV=leetcode.csv
LOG_LEVEL=INFO
MAX_PROBLEMS=0  # 0=全部，或设置测试数量如 10
```

### 4. 准备 CSV 文件

确保 `leetcode.csv` 格式如下：

```csv
"href","question","completation_rate","level"
"https://leetcode.com/problems/two-sum","1. Two Sum","56.8%","Easy"
```

### 5. 运行程序

```bash
python main.py
```

## 📁 项目结构

```
leetcode-to-notion/
├── models.py              # 数据模型
├── config.py              # 配置管理
├── scraper.py             # LeetCode 页面抓取
├── notion_blocks.py       # Notion blocks 构建器
├── notion_creator.py      # Notion 页面创建
├── main.py                # 主程序
├── requirements.txt       # 依赖项
├── .env.example          # 环境变量示例
└── README.md             # 本文件
```

## ⚙️ 配置选项

### AppConfig

- `csv_path`: CSV 文件路径
- `skip_premium`: 是否跳过 Premium 问题（默认 True）
- `max_problems`: 限制处理数量（None = 全部）
- `batch_size`: 批处理大小（默认 10）
- `log_level`: 日志级别（DEBUG/INFO/WARNING/ERROR）

### ScraperConfig

- `timeout`: 请求超时时间（秒）
- `max_retries`: 最大重试次数
- `rate_limit_delay`: 请求间隔（秒）

### NotionConfig

- `max_retries`: 最大重试次数
- `rate_limit_delay`: API 请求间隔（秒）
- `max_blocks_per_request`: 每次请求最大 blocks 数

## 🎯 使用示例

### 处理所有问题

```bash
python main.py
```

### 只处理前 10 个问题（测试）

在 `.env` 中设置：
```env
MAX_PROBLEMS=10
```

### 查看详细日志

在 `.env` 中设置：
```env
LOG_LEVEL=DEBUG
```

## 📊 输出示例

```
16:30:45 | INFO     | 加载 CSV 文件: leetcode.csv
16:30:45 | INFO     | 加载完成: 3242 个问题
16:30:45 | INFO     | 开始处理 3242 个问题
============================================================

批次 1/325
------------------------------------------------------------

[1/3242] 961 - N-Repeated Element in Size 2N Array
16:30:46 | INFO     | 抓取问题: 961 - N-Repeated Element in Size 2N Array
16:30:47 | INFO     | 抓取成功: 961
16:30:47 | INFO     | 创建页面: 961 - N-Repeated Element in Size 2N Array
16:30:48 | INFO     | ✓ 页面创建成功: https://notion.so/xxxxx
```

## ⚠️ 注意事项

1. **Premium 问题**：需要 LeetCode 订阅才能访问完整内容
2. **速率限制**：
   - LeetCode: 建议每个请求间隔 1 秒
   - Notion API: 每秒最多 3 个请求
3. **长时间运行**：处理大量问题需要较长时间，建议先用小数量测试
4. **错误处理**：程序会自动重试失败的请求，所有错误都会记录到日志

## 🐛 故障排除

### Notion API 错误

```
APIResponseError: validation_error
```
解决：检查 Integration 是否有页面访问权限

### 抓取失败

```
Max retries exceeded
```
解决：增加 `retry_delay` 或检查网络连接

### Premium 问题

```
Premium problem - subscription required
```
解决：设置 `skip_premium=True` 跳过这些问题

## 📝 设计原则

本项目遵循 **CleanRL 设计原则**：

- ✅ **单一职责**：每个模块只负责一个功能
- ✅ **显式依赖**：所有依赖通过构造函数传入
- ✅ **易于测试**：每个函数都可以独立测试
- ✅ **统一日志**：使用 loguru 处理所有异常和日志

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！