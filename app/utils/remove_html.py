"""
将带有 HTML <details> 块的聊天内容清洗为可读纯文本。

处理规则：
- 删除思维链块：匹配 <details class="think-result-details">...</details>
- 删除工具块的 HTML，但保留 <pre> 内的工具输出，并替换为明确标签：
  - 默认：工具返回：<output>
  - include_tool_name=True 时：{tool_name} 工具返回：<output>（tool_name 来自 <code>）
"""

import html
import re
from typing import Final


def _compile_details_block_re(details_class: str) -> re.Pattern[str]:
    safe = re.escape(details_class)
    return re.compile(
        rf'<details\s+class="{safe}"[\s\S]*?</details>\s*',
        re.IGNORECASE,
    )

_CODE_TAG_RE: Final[re.Pattern[str]] = re.compile(
    r"<code[^>]*>(?P<code>[\s\S]*?)</code>",
    re.IGNORECASE,
)

_PRE_TAG_RE: Final[re.Pattern[str]] = re.compile(
    r"<pre[^>]*>(?P<pre>[\s\S]*?)</pre>",
    re.IGNORECASE,
)

_MULTI_BLANK_LINES_RE: Final[re.Pattern[str]] = re.compile(r"\n{3,}")


def get_cleaned_text(
    text: str,
    *,
    think_details_class: str = "think-result-details",
    tool_details_class: str = "tool-result-details",
    decode_escaped_newlines: bool = True,
    include_tool_name: bool = False,
) -> str:
    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if decode_escaped_newlines:
        normalized = normalized.replace("\\n", "\n")

    think_details_re = _compile_details_block_re(think_details_class)
    tool_details_re = _compile_details_block_re(tool_details_class)

    without_think = think_details_re.sub("", normalized)

    def _replace_tool_block(match: re.Match[str]) -> str:
        block = match.group(0)

        tool_name = ""
        m_code = _CODE_TAG_RE.search(block)
        if m_code:
            tool_name = html.unescape(m_code.group("code")).strip()

        tool_output = ""
        m_pre = _PRE_TAG_RE.search(block)
        if m_pre:
            tool_output = html.unescape(m_pre.group("pre")).strip()

        if not tool_output:
            label = f"{tool_name} 工具返回：" if (include_tool_name and tool_name) else "工具返回："
            return f"\n\n{label}\n\n"

        if include_tool_name and tool_name:
            label = f"{tool_name} 工具返回："
        else:
            label = "工具返回："

        if "\n" in tool_output:
            return f"\n\n{label}\n{tool_output}\n\n"
        return f"\n\n{label}{tool_output}\n\n"

    replaced = tool_details_re.sub(_replace_tool_block, without_think)

    cleaned = _MULTI_BLANK_LINES_RE.sub("\n\n", replaced)
    return cleaned.strip()
