"""
联网搜索工具
"""

import json
import urllib.request

import dashscope

from pydantic import BaseModel
from dashscope import Generation
from langchain.tools import tool, ToolRuntime

class SearchTool(BaseModel):
    api_key: str
    # opensearch_url: str
    # opensearch_api_key: str

@tool
def dashscope_search(
    runtime: ToolRuntime[SearchTool],
    query: str,
) -> str:
    """使用 DashScope 提供的搜索 API 搜索互联网信息"""
    dashscope.api_key = runtime.context.api_key

    response = Generation.call(
        model='qwen-max',
        prompt=query,
        enable_search=True,
        result_format='message'
    )

    if response.status_code == 200:
        return response.output.choices[0].message.content
    else:
        return (
            "Search failed with status code: "
            f"{response.status_code}, message: {response.message}"
        )

@tool
def opensearch_search(
    runtime: ToolRuntime[SearchTool],
    query: str,
) -> str:
    """使用 阿里云-AI搜索开放平台-联网搜索服务 搜索互联网信息"""
    url = runtime.context.opensearch_url

    payload = {
        "query": query,
        "query_rewrite": True,
        "top_k": 5,
        "content_type": "snippet",
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {runtime.context.opensearch_api_key}",
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url=url, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(request, timeout=15) as resp:
        body = resp.read().decode("utf-8", errors="replace")

    data_json = json.loads(body)
    result = data_json.get("result")
    search_result = result.get("search_result")
    if len(search_result) == 0:
        return "没有搜索结果"
    lines = []
    for item in search_result:
        if not isinstance(item, dict):
            continue
        lines.append("\n".join([
            f"标题：{item.get("title", "")}",
            f"摘要：{item.get("snippet", "")}",
        ]))
    return "\n\n".join(lines) if lines else "没有搜索结果"
