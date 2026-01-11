"""
将带有 HTML <details> 块的聊天内容清洗为可读纯文本。

处理规则：
- 删除思维链块：匹配 <details class="think-result-details">...</details>
- 删除工具块的 HTML，但保留 <pre> 内的工具输出，并替换为明确标签：
  - 默认：```tool_return\n...\n```（工具名省略）
  - include_tool_name=True 时：```tool_return name="..."\n...\n```（name 来自 <code>）
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
_BACKTICKS_RE: Final[re.Pattern[str]] = re.compile(r"`+")


def get_cleaned_text(
    text: str,
    *,
    think_details_class: str = "think-result-details",
    tool_details_class: str = "tool-result-details",
    tool_call_details_class: str = "tool-call-details",
    decode_escaped_newlines: bool = True,
    include_tool_name: bool = True,
) -> str:
    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if decode_escaped_newlines:
        normalized = normalized.replace("\\n", "\n")

    think_details_re = _compile_details_block_re(think_details_class)
    tool_details_re = _compile_details_block_re(tool_details_class)
    tool_call_details_re = _compile_details_block_re(tool_call_details_class)

    without_think = think_details_re.sub("", normalized)

    def _fence_for(text: str) -> str:
        max_run = 0
        for m in _BACKTICKS_RE.finditer(text):
            max_run = max(max_run, len(m.group(0)))
        return "`" * max(3, max_run + 1)

    def _replace_details_block(match: re.Match[str], *, kind: str) -> str:
        block = match.group(0)

        tool_name = ""
        m_code = _CODE_TAG_RE.search(block)
        if m_code:
            tool_name = html.unescape(m_code.group("code")).strip()

        tool_output = ""
        m_pre = _PRE_TAG_RE.search(block)
        if m_pre:
            tool_output = html.unescape(m_pre.group("pre")).strip()

        if include_tool_name and tool_name:
            info = '{} name="{}"'.format(kind, tool_name)
        else:
            info = kind
        fence = _fence_for(tool_output)
        return f"\n\n{fence}{info}\n{tool_output}\n{fence}\n\n"

    replaced = tool_details_re.sub(lambda m: _replace_details_block(m, kind="tool_return"), without_think)
    replaced = tool_call_details_re.sub(lambda m: _replace_details_block(m, kind="tool_call"), replaced)

    cleaned = _MULTI_BLANK_LINES_RE.sub("\n\n", replaced)
    return cleaned.strip()
