"""
Notion Blocks 构建模块
职责：将 LeetCode 数据转换为 Notion blocks
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from models import LeetCodeFullData


class NotionBlockBuilder:
    """Notion Block 构建器"""
    
    MAX_TEXT_LENGTH = 2000
    
    @staticmethod
    def rich_text(
        text: str,
        bold: bool = False,
        italic: bool = False,
        code: bool = False,
        color: str = "default",
        link: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建富文本对象"""
        if len(text) > NotionBlockBuilder.MAX_TEXT_LENGTH:
            text = text[:NotionBlockBuilder.MAX_TEXT_LENGTH - 3] + "..."
        
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
    
    @staticmethod
    def heading(text: str, level: int = 1) -> Dict[str, Any]:
        """创建标题"""
        level = max(1, min(3, level))
        block_type = f"heading_{level}"
        return {
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": [NotionBlockBuilder.rich_text(text)]
            }
        }
    
    @staticmethod
    def paragraph(text: str, **kwargs) -> Dict[str, Any]:
        """创建段落"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [NotionBlockBuilder.rich_text(text, **kwargs)]
            }
        }
    
    @staticmethod
    def paragraph_with_rich_text(rich_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建带富文本的段落"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": rich_texts
            }
        }
    
    @staticmethod
    def callout(text: str, icon: str = "💡", color: str = "gray_background") -> Dict[str, Any]:
        """创建提示框"""
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [NotionBlockBuilder.rich_text(text)],
                "icon": {"emoji": icon},
                "color": color
            }
        }
    
    @staticmethod
    def quote(text: str) -> Dict[str, Any]:
        """创建引用"""
        return {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [NotionBlockBuilder.rich_text(text)]
            }
        }
    
    @staticmethod
    def code(text: str, language: str = "python") -> Dict[str, Any]:
        """创建代码块"""
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [NotionBlockBuilder.rich_text(text)],
                "language": language
            }
        }
    
    @staticmethod
    def divider() -> Dict[str, Any]:
        """创建分隔线"""
        return {
            "object": "block",
            "type": "divider",
            "divider": {}
        }
    
    @staticmethod
    def bulleted_list_item(text: str) -> Dict[str, Any]:
        """创建无序列表项"""
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [NotionBlockBuilder.rich_text(text)]
            }
        }
    
    @staticmethod
    def toggle(text: str, children: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """创建可折叠内容"""
        block = {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [NotionBlockBuilder.rich_text(text)]
            }
        }
        if children:
            block["toggle"]["children"] = children
        return block
    
    @staticmethod
    def bookmark(url: str) -> Dict[str, Any]:
        """创建书签"""
        return {
            "object": "block",
            "type": "bookmark",
            "bookmark": {
                "url": url
            }
        }


class LeetCodeNotionConverter:
    """LeetCode 到 Notion 的转换器"""
    
    def __init__(self):
        self.builder = NotionBlockBuilder
    
    def convert_problem(self, data: LeetCodeFullData) -> List[Dict[str, Any]]:
        """
        转换 LeetCode 问题为 Notion blocks
        
        Args:
            data: LeetCode 完整数据
            
        Returns:
            Notion blocks 列表
        """
        blocks = []
        problem = data.problem
        
        # 1. 问题信息头部
        blocks.extend(self._create_header(data))
        
        # 2. 问题描述
        if data.has_detail and data.detail.description:
            blocks.append(self.builder.divider())
            blocks.append(self.builder.heading("📝 Problem Description", level=2))
            blocks.append(self.builder.callout(
                data.detail.description,
                icon="📋",
                color="blue_background"
            ))
        
        # 3. 主题标签
        if data.has_detail and data.detail.topics:
            blocks.append(self.builder.divider())
            blocks.append(self.builder.heading("🏷️ Topics", level=2))
            topics_text = " • ".join(data.detail.topics)
            blocks.append(self.builder.paragraph(topics_text, bold=True, color="blue"))
        
        # 4. 代码模板区域
        blocks.append(self.builder.divider())
        blocks.append(self.builder.heading("💻 Solution", level=2))
        blocks.append(self.builder.paragraph("Write your solution here:"))
        
        # Python 模板
        python_template = self._get_python_template(problem.problem_title)
        blocks.append(self.builder.code(python_template, "python"))
        
        # 时间复杂度分析
        blocks.append(self.builder.paragraph(""))
        blocks.append(self.builder.paragraph("Time Complexity Analysis:", bold=True))
        blocks.append(self.builder.bulleted_list_item("Time: O(?)"))
        blocks.append(self.builder.bulleted_list_item("Space: O(?)"))
        
        # 5. 提示（可折叠）
        if data.has_detail and data.detail.hints:
            blocks.append(self.builder.divider())
            blocks.append(self.builder.heading("💡 Hints", level=2))
            for i, hint in enumerate(data.detail.hints, 1):
                blocks.append(self.builder.quote(f"Hint {i}: {hint}"))
        
        # 6. 相似问题
        if data.has_detail and data.detail.similar_questions:
            blocks.append(self.builder.divider())
            blocks.append(self.builder.heading("🔗 Similar Questions", level=2))
            similar_text = "\n".join(f"• {q}" for q in data.detail.similar_questions)
            blocks.append(self.builder.callout(
                similar_text,
                icon="🔍",
                color="gray_background"
            ))
        
        # 7. 笔记区域
        blocks.append(self.builder.divider())
        blocks.append(self.builder.heading("📓 Notes", level=2))
        blocks.append(self.builder.paragraph("Add your notes here..."))
        
        logger.debug(f"转换完成: {len(blocks)} blocks")
        return blocks
    
    def _create_header(self, data: LeetCodeFullData) -> List[Dict[str, Any]]:
        """创建问题头部信息"""
        blocks = []
        problem = data.problem
        
        # 难度图标
        level_icons = {
            "Easy": "🟢",
            "Med.": "🟡",
            "Hard": "🔴"
        }
        icon = level_icons.get(problem.level, "⚪")
        
        # 基本信息 callout
        info_text = (
            f"{icon} Difficulty: {problem.level}\n"
            f"✅ Completion Rate: {problem.completion_rate}\n"
            f"🔢 Problem ID: {problem.problem_id}"
        )
        blocks.append(self.builder.callout(info_text, icon=icon, color="blue_background"))
        
        # LeetCode 链接
        blocks.append(self.builder.paragraph_with_rich_text([
            self.builder.rich_text("🔗 ", bold=True),
            self.builder.rich_text("View on LeetCode", link=problem.href, color="blue")
        ]))
        
        # Premium 警告
        if data.detail and data.detail.is_premium:
            blocks.append(self.builder.callout(
                "⚠️ This is a Premium problem. Detailed information requires subscription.",
                icon="🔒",
                color="yellow_background"
            ))
        
        return blocks
    
    def _get_python_template(self, title: str) -> str:
        """生成 Python 代码模板"""
        class_name = "Solution"
        method_name = "solve"
        
        # 尝试从标题生成方法名
        title_parts = title.lower().replace('-', ' ').split()
        if title_parts:
            method_name = ''.join(word.capitalize() for word in title_parts[:3])
            method_name = method_name[0].lower() + method_name[1:]
        
        template = f'''class {class_name}:
    def {method_name}(self, nums: List[int]) -> int:
        """
        Your solution here
        
        Args:
            nums: Input array
            
        Returns:
            Result
        """
        # Write your code here
        pass


# Test cases
if __name__ == "__main__":
    solution = {class_name}()
    
    # Example 1
    nums = []
    result = solution.{method_name}(nums)
    print(f"Result: {{result}}")
'''
        return template