"""
一个智能体
"""

import os
import asyncio

from typing import List, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware


# 加载模型配置
# load_dotenv("../.env")

async def get_agent():
    # Ensure env is loaded
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    from tools.tool_math import add, subtract, multiply, divide
    from tools.tool_search import dashscope_search
    from prompts.prompt_base import get_system_prompt_base
    llm = ChatOpenAI(
        model="kimi-k2-thinking",
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        max_retries=3,
        timeout=30,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": True,
            }
        }
    )

    # 接入 MCP
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    client = MultiServerMCPClient(  
        {
            "role-play": {
                "command": "python",
                "args": [os.path.join(app_root, "mcp/role_play.py")],
                "transport": "stdio",
            },
            "code-execution": {
                "command": "python",
                "args": [os.path.join(app_root, "mcp/code_execution.py")],
                "transport": "stdio",
            },
        }
    )
    mcp_tools = await client.get_tools()

    # 创建 subagent
    @tool(
        "subagent",
        description="通用子智能体 (subagent)，拥有独立上下文空间，支持联网搜索"
    )
    def call_subagent(query: str):
        subagent = create_agent(
            model=llm,
            tools=[dashscope_search],
            name="subagent",
        )
        result = subagent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        return result["messages"][-1].content

    # 创建智能体
    agent = create_agent(
        model=llm,
        tools=mcp_tools + [add, subtract, multiply, divide, dashscope_search, call_subagent],
        system_prompt=get_system_prompt_base(),
        middleware=[
            SummarizationMiddleware(
                model=llm,
                trigger=("tokens", 2000),
                keep=("messages", 7),
            ),
            TodoListMiddleware(
                system_prompt="\n".join([
                    "当用户请求较为复杂且可以拆分为多个子任务时，创建任务列表。",
                    "当用户主动要求创建任务列表 (todo list) 时，必须创建任务列表。",
                    "\n以下 3 种情形无需创建任务列表：",
                    "1. 任务过于简单时，无需创建",
                    "2. 任务数量小于 3 个时，无需创建",
                    "3. 纯文字分析、无工具调用时，无需创建",
                    "\n使用 write_todos 工具管理任务列表时，遵循以下规则：",
                    "1. 任务分解：应满足“低耦合，高内聚”的原则",
                    "2. 前置任务：确保当前任务的前置依赖已完成（如有）",
                    "3. 完成标准：每个任务应该有明确的验收标准",
                    "4. 状态流转：在任务状态改变时立即更新（待办/进行中/完成/取消）",
                    "\n每完成 1 个任务，用 Markdown 表格向用户展示当前任务列表，格式如下：",
                    "| ID | 任务 | 状态 | ",
                    "| -- | -- | -- |",
                    "| 1 | 任务1 | 完成 |",
                    "| 2 | 任务2 | 进行中 |",
                    "| 3 | 任务3 | 待办 |",
                ])
            ),
        ],
    )

    return agent


async def generate_response(message: str,
                            history: List[Dict[str, str]]
):
    from tools.tool_search import SearchTool

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})

    messages = history[:-1]

    agent = await get_agent()

    async for token, metadata in agent.astream(
        {"messages": messages},
        stream_mode="messages",
        context=SearchTool(api_key=os.getenv("DASHSCOPE_API_KEY")),
    ):
        print("=======================")
        print("token:", token)
        print("-----------------------")
        print("metadata:", metadata)
        

async def get_agent_minimal():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

    from tools.tool_search import dashscope_search

    llm = ChatOpenAI(
        model="qwen3-coder-plus",
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        max_retries=3,
        timeout=30,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": True,
            }
        }
    )

    return create_agent(
        model=llm,
        tools=[dashscope_search],
    )


async def generate_response_minimal(message: str,
                                    history: List[Dict[str, str]]
):
    from tools.tool_search import SearchTool

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})

    messages = history[:-1]
    agent = await get_agent_minimal()

    async for token, metadata in agent.astream(
        {"messages": messages},
        stream_mode="messages",
        context=SearchTool(api_key=os.getenv("DASHSCOPE_API_KEY")),
    ):
        print("=======================")
        print("token:", token)
        print("-----------------------")
        print("metadata:", metadata)

async def get_agent_minimal_dashscope():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

    llm = ChatOpenAI(
        model="kimi-k2-thinking",
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        max_retries=3,
        timeout=30,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": True,
            }
        }
    )

    return create_agent(
        model=llm,
    )


async def probe_values_mode_thinking(message: str):
    from tools.tool_search import SearchTool

    agent = await get_agent_minimal_dashscope()
    messages = [{"role": "user", "content": message}]

    last_values_snapshot = None
    last_values_has_reasoning_type = False
    last_values_has_reasoning_field = False
    last_values_has_reasoning_text = False

    async for mode, payload in agent.astream(
        {"messages": messages},
        stream_mode=["messages", "values"],
        context=SearchTool(api_key=os.getenv("DASHSCOPE_API_KEY")),
    ):
        if mode == "messages":
            token, metadata = payload
            if token.content:
                dashscope_type = token.response_metadata.get("dashscope_type") if getattr(token, "response_metadata", None) else None
                print(f"[messages] node={metadata.get('langgraph_node')} type={dashscope_type} text={token.content[:120]!r}")
        elif mode == "values":
            state = payload
            state_messages = state.get("messages") if isinstance(state, dict) else None
            if not state_messages:
                continue
            last_message = state_messages[-1]

            content = getattr(last_message, "content", None)
            response_metadata = getattr(last_message, "response_metadata", None) or {}
            additional_kwargs = getattr(last_message, "additional_kwargs", None) or {}

            content_str = str(content)
            if content_str == last_values_snapshot:
                continue
            last_values_snapshot = content_str

            dashscope_type = response_metadata.get("dashscope_type")
            has_reasoning_type = dashscope_type == "reasoning"
            has_reasoning_field = bool(additional_kwargs.get("reasoning_content"))
            has_reasoning_text = "reasoning_content" in content_str or "思考" in content_str

            last_values_has_reasoning_type = last_values_has_reasoning_type or has_reasoning_type
            last_values_has_reasoning_field = last_values_has_reasoning_field or has_reasoning_field
            last_values_has_reasoning_text = last_values_has_reasoning_text or has_reasoning_text

            print(
                "[values] "
                f"last_message={type(last_message).__name__} "
                f"dashscope_type={dashscope_type!r} "
                f"content_preview={content_str[:120]!r} "
                f"additional_kwargs_keys={sorted(list(additional_kwargs.keys()))[:12]}"
            )

    print(
        "[values-summary] "
        f"dashscope_type_reasoning={last_values_has_reasoning_type} "
        f"additional_kwargs_has_reasoning_content={last_values_has_reasoning_field} "
        f"content_looks_like_reasoning={last_values_has_reasoning_text}"
    )


if __name__ == "__main__":
    import os
    import sys
    import asyncio

    # 将项目根目录添加到 Python 路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(current_dir)
    sys.path.insert(0, app_dir)

    asyncio.run(probe_values_mode_thinking("请先思考再回答：用一句话解释为什么 1+1=2。"))
