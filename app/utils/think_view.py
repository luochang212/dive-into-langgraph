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

    return "\n".join(
        [
            '<details class="think-result-details">',
            '<summary class="think-result-summary">',
            '<div class="think-result-title"> 💭 Thinking</div>',
            '<svg class="think-result-icon" width="20" height="20" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"></polyline></svg>',
            "</summary>",
            '<pre class="think-result-pre">',
            f"\n{html.escape(think_content)}",
            "</pre>",
            "</details>\n\n",
        ]
    )
