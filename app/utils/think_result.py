# -*- coding: utf-8 -*-

"""
优化思考过程内容显示
"""

import html


def format_think_result(think_content: str) -> str:
    """
    格式化思考过程内容，返回 HTML 字符串。

    :param think_content: 思考过程内容
    :return: 格式化后的 HTML 字符串
    """
    if not think_content:
        return ""

    return "\n".join([
        '<details class="think-result-details" style="border: 1px solid #555; border-radius: 8px; padding: 10px; margin: 10px 0; background-color: #2a2a3a;">',
        '<summary class="think-result-summary" style="display: flex; justify-content: space-between; align-items: center; list-style: none;">',
        '<div style="display: flex; align-items: center;"> 💭 Thinking</div>',
        '<svg class="think-result-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>',
        '</summary>',
        '<pre style="margin-top: 10px; padding: 10px; background-color: #1e1e2e; border-radius: 4px; color: #bbb; font-family: monospace; white-space: pre-wrap; max-height: 400px; overflow-y: auto; border: 1px solid #333; font-size: 0.9em;">',
        f'\n{html.escape(think_content)}',
        '</pre>',
        '</details>\n\n',
    ])
