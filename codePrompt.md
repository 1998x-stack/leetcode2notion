
leetcode.csv
```
"href","question","completation_rate","level"
"https://leetcode.com/problems/n-repeated-element-in-size-2n-array?envType=daily-question&envId=2026-01-02","961. N-Repeated Element in Size 2N Array","79.2%","Easy"
"https://leetcode.com/problems/two-sum","1. Two Sum","56.8%","Easy"
"https://leetcode.com/problems/add-two-numbers","2. Add Two Numbers","47.6%","Med."
"https://leetcode.com/problems/longest-substring-without-repeating-characters","3. Longest Substring Without Repeating Characters","38.1%","Med."
"https://leetcode.com/problems/median-of-two-sorted-arrays","4. Median of Two Sorted Arrays","45.5%","Hard"
"https://leetcode.com/problems/longest-palindromic-substring","5. Longest Palindromic Substring","37.0%","Med."
"https://leetcode.com/problems/zigzag-conversion","6. Zigzag Conversion","53.1%","Med."
"https://leetcode.com/problems/reverse-integer","7. Reverse Integer","31.2%","Med."
"https://leetcode.com/problems/string-to-integer-atoi","8. String to Integer (atoi)","20.3%","Med."
"https://leetcode.com/problems/palindrome-number","9. Palindrome Number","60.0%","Easy"
...
```


any href(https://leetcode.com/problems/zigzag-conversion) you can get
```
description: `.gap-1+ div .elfjS`
topics: `.pl-7 .text-text-secondary`
hints: `.transition-all .elfjS`
similar_questions`.dark\:hover\:text-dark-blue-s .dark\:hover\:text-dark-blue-s`
```
but notice: some hrefs can not get in because you need subscribe


please based on codes above
given notion_token and page_id
design pages for all leetcode problems based on leetcode.csv given
scrape leetcode pages based hrefs
and extract the info
and make full use of Notion 元素
```
- heading_1/2/3: 标题
- paragraph: 段落（支持富文本）
- callout: 提示框（摘要、警告等）
- quote: 引用
- code: 代码块
- equation: 数学公式
- table: 表格
- bulleted_list_item: 无序列表
- numbered_list_item: 有序列表
- divider: 分隔线
- toggle: 可折叠内容
- image: 图片
- bookmark: 链接预览
```

build beautifule notion pages for all leetcode problems in leetcode.csv given

notice:
build quote blocks for hints if exist
build callout blocks for similar questions if exist
build callout blocks for description if exist
build code blocks for page users to solve the problems



``` 遵循CleanRL设计原则:单一职责、显式依赖、易于测试。 use loguru for all exceptions, logger.info(error_message) `` exc_type, exc_value, exc_traceback = sys.exc_info() error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback)) `` ```
