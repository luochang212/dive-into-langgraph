"""
联网搜索工具
"""

from langchain.tools import tool, ToolRuntime
from openai import OpenAI
from tools.tool_runtime import ToolSchema


@tool
def dashscope_search(
    query: str,
    runtime: ToolRuntime[ToolSchema],
) -> str:
    """使用 DashScope 提供的搜索 API 搜索互联网信息"""
    client = OpenAI(
        api_key=runtime.context.api_key,
        base_url=runtime.context.base_url,
    )
    response = client.responses.create(
        model=runtime.context.model,
        input=query,
        tools=[{"type": "web_search"}],
    )
    return response.output_text
