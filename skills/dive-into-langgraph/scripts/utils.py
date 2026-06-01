#!/usr/bin/env python3
"""
LangChain & LangGraph 通用工具函数
"""

import os

from langchain_openai import ChatOpenAI


def create_llm(
    model: str = "qwen3.5-plus",
    **kwargs,
) -> ChatOpenAI:
    """使用 ChatOpenAI 创建 LLM"""
    return ChatOpenAI(
        model=model,
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        **kwargs,
    )


def list_agent_tools(agent) -> str:
    """获取 Agent 的工具列表"""
    node = agent.get_graph().nodes["tools"]
    tools = list(node.data.tools_by_name.values())

    lines = []
    for tool in tools:
        desc = (tool.description or "").split('\n')[0]
        lines.append(f"- `{tool.name}`: {desc}")
    return "\n".join(lines)


async def stream_messages(agent, messages: dict):
    """流式输出 - messages 模式"""
    async for token, _ in agent.astream(
            messages,
            stream_mode="messages",
    ):
        if token.content:
            print(token.content, end="", flush=True)


def print_section(title: str):
    """打印分隔线"""
    print()
    print("=" * 50)
    print(f"  {title}")
    print("=" * 50)
