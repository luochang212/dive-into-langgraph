# -*- coding: utf-8 -*-

"""
优化工具调用结果显示
"""

import html
import json
from typing import Any

def _to_display_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        try:
            return json.dumps(value, ensure_ascii=False, indent=2, default=str)
        except Exception:
            return str(value)
    if isinstance(value, (list, tuple, set)):
        parts = [_to_display_text(item) for item in value]
        return "\n".join(parts)
    return str(value)


def format_tool_result(tool_name: str, tool_output: Any) -> str:
    """
    格式化工具调用结果，返回 HTML 字符串。

    :param tool_name: 工具名称
    :param tool_output: 工具调用输出
    :return: 格式化后的 HTML 字符串
    """
    safe_tool_name = html.escape(tool_name)
    safe_tool_output = html.escape(_to_display_text(tool_output))
    return "\n".join([
        '<details class="tool-result-details">',
        '<summary class="tool-result-summary">',
        f'<div class="tool-result-title"> 🔧 Tool: <code class="tool-result-name">{safe_tool_name}</code></div>',
        '<svg class="tool-result-icon" width="20" height="20" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>',
        '</summary>',
        '<pre class="tool-result-pre">',
        f"\n{safe_tool_output}",
        '</pre>',
        '</details>\n\n',
    ])
