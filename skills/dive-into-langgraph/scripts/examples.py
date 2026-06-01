#!/usr/bin/env python3
"""
LangChain & LangGraph 示例脚本
"""

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent

from utils import (
    create_llm,
    stream_messages,
    list_agent_tools,
    print_section,
)
from tools.tool_math import (
    add,
    subtract,
    multiply,
    divide,
    safe_eval,
)


def simple_invoke_example(agent):
    print_section("简单调用")
    query = "你好"
    print(f"😄 {query}")
    response = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    print(f"🤖 {response["messages"][-1].content}")


def math_tool_example(agent):
    print_section("数学工具调用")
    query = "计算 log(99, 3) + 3"
    print(f"😄 {query}")
    response = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    print(f"🤖 {response["messages"][-1].content}")


def list_tools_example(agent):
    print_section("打印 Agent 的工具列表")
    print(list_agent_tools(agent))


def stream_messages_example(agent):
    print_section("流式调用 - messages 模式")
    query = "介绍抹茶布丁的做法，字数 100 字左右"
    print(f"😄 {query}")
    print("🤖 ", end="")
    asyncio.run(stream_messages(agent, {"messages": [{"role": "user", "content": query}]}))


def main():
    """主函数"""
    # 从 .env 文件加载环境变量
    load_dotenv()

    # 创建模型
    llm = create_llm()

    # 创建 Agent
    agent = create_agent(llm)
    agent_with_tools = create_agent(
        llm,
        tools=[add, subtract, multiply, divide, safe_eval]
    )

    # 运行示例
    simple_invoke_example(agent)
    math_tool_example(agent_with_tools)
    list_tools_example(agent_with_tools)
    stream_messages_example(agent)


if __name__ == "__main__":
    main()
