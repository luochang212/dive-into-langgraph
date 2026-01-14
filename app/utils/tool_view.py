# -*- coding: utf-8 -*-

"""
优化工具调用输入/结果显示
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


def _maybe_pretty_json(text: str) -> str:
    if not isinstance(text, str):
        return _to_display_text(text)
    stripped = text.strip()
    if not stripped:
        return ""
    if not ((stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]"))):
        return text
    try:
        parsed = json.loads(stripped)
    except Exception:
        return text
    try:
        return json.dumps(parsed, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(parsed)


def format_tool_call(tool_name: str, tool_args: Any) -> str:
    safe_tool_name = html.escape(tool_name)
    if isinstance(tool_args, str):
        display_args = _maybe_pretty_json(tool_args)
    else:
        display_args = _to_display_text(tool_args)
    safe_tool_args = html.escape(display_args)
    return "\n".join([
        '<details class="tool-call-details">',
        '<summary class="tool-call-summary">',
        f'<div class="tool-call-title"> 🔧 Tool Call: <code class="tool-call-name">{safe_tool_name}</code></div>',
        '<svg class="tool-call-icon" width="20" height="20" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>',
        '</summary>',
        '<pre class="tool-call-pre">',
        f"\n{safe_tool_args}",
        '</pre>',
        '</details>\n\n',
    ])


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
        f'<div class="tool-result-title"> 📁 Tool Result: <code class="tool-result-name">{safe_tool_name}</code></div>',
        '<svg class="tool-result-icon" width="20" height="20" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>',
        '</summary>',
        '<pre class="tool-result-pre">',
        f"\n{safe_tool_output}",
        '</pre>',
        '</details>\n\n',
    ])
