"""
LeetCode Notion 转换模块
职责：将 LeetCode 问题转换为丰富的 Notion blocks
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
import sys
import traceback
from typing import List, Dict, Any, Optional
from loguru import logger

from leetcode_models import LeetCodeProblem, Difficulty


class LeetCodeNotionConverter:
    """
    LeetCode 到 Notion 转换器
    
    将 LeetCode 问题转换为美观的 Notion 页面内容
    """
    
    MAX_TEXT_LENGTH = 2000
    
    def __init__(self):
        """初始化转换器"""
        pass
    
    @staticmethod
    def _rich_text(
        text: str,
        bold: bool = False,
        italic: bool = False,
        code: bool = False,
        color: str = "default",
        link: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建富文本对象"""
        if len(text) > LeetCodeNotionConverter.MAX_TEXT_LENGTH:
            text = text[:LeetCodeNotionConverter.MAX_TEXT_LENGTH - 3] + "..."
        
        result = {
            "type": "text",
            "text": {"content": text}
        }
        
        if link:
            result["text"]["link"] = {"url": link}
        
        annotations = {}
        if bold:
            annotations["bold"] = True
        if italic:
            annotations["italic"] = True
        if code:
            annotations["code"] = True
        if color != "default":
            annotations["color"] = color
        
        if annotations:
            result["annotations"] = annotations
        
        return result
    
    def convert_problem(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """
        转换 LeetCode 问题为 Notion blocks
        
        Args:
            problem: LeetCode 问题
            
        Returns:
            Notion blocks 列表
        """
        blocks = []
        
        try:
            # 1. 头部信息卡片
            blocks.extend(self._create_header(problem))
            
            # 2. 问题描述
            if problem.description:
                blocks.extend(self._create_description(problem))
            
            # 3. 解题代码区
            blocks.extend(self._create_code_section(problem))
            
            # 4. 提示（如果有）
            if problem.hints:
                blocks.extend(self._create_hints(problem))
            
            # 5. 相似问题（如果有）
            if problem.similar_questions:
                blocks.extend(self._create_similar_questions(problem))
            
            # 6. 主题标签（如果有）
            if problem.topics:
                blocks.extend(self._create_topics(problem))
            
            # 7. 底部链接
            blocks.extend(self._create_footer(problem))
            
            logger.debug(f"转换完成: {problem.display_title}, {len(blocks)} blocks")
            
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logger.error(f"转换失败: {error_message}")
        
        return blocks
    
    def _create_header(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """创建头部信息"""
        blocks = []
        
        # 难度和完成率 callout
        emoji = problem.difficulty_emoji
        color = problem.difficulty.get_color()
        
        info_text = (
            f"{emoji} Difficulty: {problem.difficulty.value}\n"
            f"📊 Acceptance Rate: {problem.completion_rate}\n"
            f"🔢 Problem Number: {problem.number}"
        )
        
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [self._rich_text(info_text)],
                "icon": {"emoji": emoji},
                "color": color
            }
        })
        
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        return blocks
    
    def _create_description(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """创建问题描述"""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [self._rich_text("📝 Problem Description", bold=True)],
                "color": "blue"
            }
        })
        
        # 使用 callout 显示描述
        description = problem.description
        if len(description) > self.MAX_TEXT_LENGTH:
            # 分段处理长描述
            chunks = self._split_text(description)
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [self._rich_text(chunks[0])],
                    "icon": {"emoji": "📄"},
                    "color": "gray_background"
                }
            })
            
            # 剩余部分用段落
            for chunk in chunks[1:]:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [self._rich_text(chunk)]
                    }
                })
        else:
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [self._rich_text(description)],
                    "icon": {"emoji": "📄"},
                    "color": "gray_background"
                }
            })
        
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        return blocks
    
    def _create_code_section(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """创建解题代码区"""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [self._rich_text("💻 Solution", bold=True)],
                "color": "green"
            }
        })
        
        # Python 代码模板
        code_template = f"""# {problem.display_title}
# Difficulty: {problem.difficulty.value}
# Acceptance: {problem.completion_rate}

class Solution:
    def solve(self):
        # Write your solution here
        pass


# Test cases
if __name__ == "__main__":
    solution = Solution()
    # Add your test cases here
    pass
"""
        
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [self._rich_text(code_template)],
                "language": "python"
            }
        })
        
        # 添加多语言代码块选项
        blocks.append({
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [self._rich_text("🌐 More Language Templates")],
                "children": [
                    {
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [self._rich_text("JavaScript")]
                        }
                    },
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [self._rich_text(
                                f"// {problem.display_title}\n"
                                f"// Difficulty: {problem.difficulty.value}\n\n"
                                "var solve = function() {\n"
                                "    // Write your solution here\n"
                                "};"
                            )],
                            "language": "javascript"
                        }
                    },
                    {
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [self._rich_text("Java")]
                        }
                    },
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [self._rich_text(
                                f"// {problem.display_title}\n"
                                f"// Difficulty: {problem.difficulty.value}\n\n"
                                "class Solution {\n"
                                "    public void solve() {\n"
                                "        // Write your solution here\n"
                                "    }\n"
                                "}"
                            )],
                            "language": "java"
                        }
                    }
                ]
            }
        })
        
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        return blocks
    
    def _create_hints(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """创建提示部分"""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [self._rich_text("💡 Hints", bold=True)],
                "color": "yellow"
            }
        })
        
        # 每个提示用 quote block
        for i, hint in enumerate(problem.hints, 1):
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [
                        self._rich_text(f"Hint {i}: ", bold=True),
                        self._rich_text(hint)
                    ],
                    "color": "yellow_background"
                }
            })
        
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        return blocks
    
    def _create_similar_questions(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """创建相似问题部分"""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [self._rich_text("🔗 Similar Questions", bold=True)],
                "color": "purple"
            }
        })
        
        # 使用 callout 展示相似问题
        similar_text = "\n".join([
            f"• {sq.title}"
            for sq in problem.similar_questions
        ])
        
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [self._rich_text(similar_text)],
                "icon": {"emoji": "🔗"},
                "color": "purple_background"
            }
        })
        
        # 每个相似问题的链接
        for sq in problem.similar_questions:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        self._rich_text("➜ ", color="purple"),
                        self._rich_text(sq.title, link=sq.url, color="blue")
                    ]
                }
            })
        
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        return blocks
    
    def _create_topics(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """创建主题标签部分"""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [self._rich_text("🏷️ Topics", bold=True)]
            }
        })
        
        # 用 bullet list 显示主题
        for topic in problem.topics:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [self._rich_text(topic, code=True)]
                }
            })
        
        return blocks
    
    def _create_footer(self, problem: LeetCodeProblem) -> List[Dict[str, Any]]:
        """创建底部链接"""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        # 链接 bookmark
        blocks.append({
            "object": "block",
            "type": "bookmark",
            "bookmark": {
                "url": problem.href,
                "caption": [self._rich_text(f"View on LeetCode: {problem.display_title}")]
            }
        })
        
        # 资源链接
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    self._rich_text("📚 Resources: ", bold=True),
                    self._rich_text("Solutions", link=f"{problem.href}/solutions/", color="blue"),
                    self._rich_text(" | "),
                    self._rich_text("Discuss", link=f"{problem.href}/discuss/", color="blue"),
                ]
            }
        })
        
        return blocks
    
    def _split_text(self, text: str) -> List[str]:
        """分割长文本"""
        if len(text) <= self.MAX_TEXT_LENGTH:
            return [text]
        
        chunks = []
        remaining = text
        
        while remaining:
            if len(remaining) <= self.MAX_TEXT_LENGTH:
                chunks.append(remaining)
                break
            
            chunk = remaining[:self.MAX_TEXT_LENGTH]
            
            # 尝试在句子边界分割
            last_period = max(
                chunk.rfind('. '),
                chunk.rfind('\n'),
                chunk.rfind('。'),
            )
            
            if last_period > self.MAX_TEXT_LENGTH * 0.5:
                chunk = chunk[:last_period + 1]
            
            chunks.append(chunk.strip())
            remaining = remaining[len(chunk):].strip()
        
        return chunks