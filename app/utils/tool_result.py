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
        # # 移动到 utils.web_ui
        # '<style>',
        # '.tool-result-summary::-webkit-details-marker { display: none; }',
        # '.tool-result-summary { list-style: none; display: flex; justify-content: space-between; align-items: center; cursor: pointer; font-weight: bold; color: #eee; outline: none; }',
        # '.tool-result-details[open] .tool-result-icon { transform: rotate(180deg); }',
        # '.tool-result-icon { transition: transform 0.2s ease; }',
        # '</style>',
        '<details class="tool-result-details" style="border: 1px solid #444; border-radius: 8px; padding: 10px; margin: 10px 0; background-color: #2b2b2b;">',
        '<summary class="tool-result-summary" style="display: flex; justify-content: space-between; align-items: center; list-style: none;">',
        f'<div style="display: flex; align-items: center;"> 🔧 Tool: <code style="color: #ffaa00; background: none; border: none; margin-left: 5px;">{safe_tool_name}</code></div>',
        '<svg class="tool-result-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#eee" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>',
        '</summary>',
        '<pre style="margin-top: 10px; padding: 10px; background-color: #1e1e1e; border-radius: 4px; color: #ddd; font-family: monospace; white-space: pre-wrap; max-height: 400px; overflow-y: auto; border: 1px solid #333;">',
        f"\n{safe_tool_output}",
        '</pre>',
        '</details>\n\n',
    ])
