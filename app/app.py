"""
一个智能体
"""

import os
import uuid
import asyncio
import textwrap
import argparse

from typing import List, Dict, AsyncIterator, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware, dynamic_prompt, ModelRequest
from prompts import middleware_todolist, subagent_search, prompt_enhance
from utils.web_ui import create_ui, theme, custom_css
from utils.tool_view import format_tool_call, format_tool_result
from utils.remove_html import get_cleaned_text
from tools.tool_runtime import ToolSchema
from tools.tool_sci import calculator
from tools.tool_search import dashscope_search
from tools.tool_role import role_play
from config.mcp_config import get_mcp_dict


# 加载模型配置
# 注意‼️：请先在 .env 中配置 DASHSCOPE_API_KEY
load_dotenv()


# 是否清洗历史对话记录中的 HTML 内容
REMOVE_HTML = False


# # 全局变量
_agent = None  # 全局 Agent 实例


# 加载 LLM 模型
# ==================== 使用 DashScope ====================
# 阿里 DashScope 目前有免费额度，支持以下模型：
#   kimi-k2-thinking / deepseek-v3.2 / glm-4.7 / qwen3-coder-plus-2025-07-22
# 如果觉得卡，可以使用付费模型：
#   qwen3-max / qwen3-max-preview / qwen3-coder-plus
llm = ChatOpenAI(
    model="qwen3-coder-plus",
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    timeout=30,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": True,
        }
    }
)
# ==================== 使用 Ark ====================
# # 字节火山方舟 目前有免费额度，支持以下模型：
# #   deepseek-v3-2-251201 / kimi-k2-thinking-251104 / doubao-seed-1-8-251228
# llm = ChatOpenAI(
#     model="deepseek-v3-2-251201",
#     base_url=os.getenv("ARK_BASE_URL"),
#     api_key=os.getenv("ARK_API_KEY"),
#     max_retries=1,
#     timeout=30,
# )
# ==================== 使用 Ollama ====================
# # 使用前需要：
# # 1. 下载 qwen3:4b 模型 
# #     ollama pull qwen3:4b
# # 2. 开启 Ollama 服务
# #     OLLAMA_HOST=0.0.0.0:11435 ollama serve
# llm = ChatOpenAI(
#     model="qwen3:4b",
#     base_url="http://127.0.0.1:11435/v1",
#     api_key="-",  # 非空
#     max_retries=1,
#     timeout=30,
#     temperature=0.7,
#     top_p=0.9,
#     extra_body={
#         "chat_template_kwargs": {
#             "enable_thinking": True,
#         }
#     }
# )
# ==================== The End ====================


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    """Agent 的动态系统提示词"""
    return prompt_enhance.get_system_prompt()


@dynamic_prompt
def dynamic_system_prompt_subagent_search(request: ModelRequest) -> str:
    """Search Subagent 的动态系统提示词"""
    return subagent_search.get_system_prompt()


# 创建 search subagent
search_subagent = create_agent(
    model=llm,
    tools=[dashscope_search],
    middleware=[dynamic_system_prompt_subagent_search],
)


@tool(
    "subagent:search-brief",
    description=subagent_search.get_tool_description(),
)
async def search_brief(
    query: str,
    runtime: ToolRuntime[ToolSchema],
) -> str:
    """获取搜索结果的摘要"""
    result = await search_subagent.ainvoke(
        {"messages": [{"role": "user", "content": query}]},
        config={"configurable": {"thread_id": str(uuid.uuid4())}},
        context=runtime.context,
    )
    return result["messages"][-1].content


async def get_agent():
    """获取全局 Agent 实例"""
    global _agent
    if _agent is None:
        client = MultiServerMCPClient(
            {k: v for k, v in get_mcp_dict().items() if k in {
                # 开启的 MCP
                "code-execution:stdio",
                # # 未开启的 MCP
                # "antv-chart:stdio",
                # "filesystem:stdio",
                # "amap-maps:http",
            }}
        )

        # 获取 MCP 工具
        mcp_tools = await client.get_tools()

        # 创建智能体
        _agent = create_agent(
            model=llm,
            tools=mcp_tools + [calculator, role_play, dashscope_search, search_brief],
            middleware=[
                dynamic_system_prompt,
                SummarizationMiddleware(
                    model=llm,
                    trigger=("tokens", 2000),
                    keep=("messages", 7),
                ),
                TodoListMiddleware(
                    system_prompt=middleware_todolist.get_system_prompt()
                ),
            ],
        )
    return _agent


def get_tools():
    """获取 Agent 的工具列表"""
    agent = asyncio.run(get_agent())
    node = agent.get_graph().nodes["tools"]
    tools = list(node.data.tools_by_name.values())

    # 优化工具展示
    if len(tools) < 13:
        # 当工具不多时，展示工具描述
        lines = []
        for tool in tools:
            desc = (tool.description or "").split('\n')[0]
            lines.append(f"- `{tool.name}`: {desc}")
        return "\n".join(lines)
    else:
        # 当工具过多时，仅展示工具名称
        tool_names = [tool.name for tool in tools]
        wrapped_text = textwrap.fill(" / ".join(tool_names), width=110)
        return f"\n```text\n{wrapped_text}\n```\n"


def get_greeting():
    """获取 Agent 的自我介绍"""
    greeting = ""
    try:
        tools_info = get_tools()
        greeting = "\n".join([
            "你好！我是你的智能助手，可以使用的工具包括：",
            tools_info,
            "\n请问有什么可以帮你的吗？",
        ])
    except Exception as e:
        print(f"获取工具列表时出错: {e}")
        greeting = "你好！我是你的智能助手。\n请问有什么可以帮你的吗？"
    return greeting


def error_summary(err: Exception, limit: int = 500) -> str:
    """总结 Agent 运行错误"""
    import traceback

    # 获取完整报错信息
    full_trace = "".join(traceback.format_exception(type(err), err, err.__traceback__))
    full_trace = full_trace[-5000:]  # 避免报错信息过长

    summary = ""
    try:
        # 优先输出日志摘要
        abstract = llm.invoke("\n".join([
            full_trace,
            "---",
            "以上是 LangChain Agent 的报错信息，请简述报错原因：",
        ]))
        summary = f"\n ⚠️ 发生错误，以下是摘要信息：\n{abstract}"
    except Exception:
        # 输出摘要失败，降级为输出原始日志
        summary = f"\n ⚠️ 发生错误，以下是原始日志：\n{full_trace[:limit]}"

    return summary


async def _agent_events_optimize(
    agent,
    messages,
    history: List[Dict[str, str]],
) -> AsyncIterator[Tuple[str, List[Dict[str, str]]]]:
    """优化显示，处理 messages 和 values 事件流"""
    async for mode, payload in agent.astream(
        {"messages": messages},
        stream_mode=["messages", "values"],
        context=ToolSchema(
            base_url=os.getenv("DASHSCOPE_BASE_URL"),
            api_key=os.getenv("DASHSCOPE_API_KEY")
        ),
    ):
        if mode == "messages":
            token, metadata = payload
            current_node = metadata["langgraph_node"]
            if current_node == "model":
                # 模型回复
                if token.content:
                    history[-1]["content"] += token.content
                    yield "", history
            elif current_node == "tools":
                # 避免与搜索子智能体的输出重复
                if token.name in ["subagent:search-brief"]:
                    continue
                # 工具调用结果
                if token.content:
                    history[-1]["content"] += format_tool_result(token.name, token.content)
                    yield "", history
        elif mode == "values":
            state = payload
            state_messages = state.get("messages") if isinstance(state, dict) else None
            if not state_messages:
                continue
            last_message = state_messages[-1]

            # 工具调用入参
            tool_calls = getattr(last_message, "tool_calls", None)
            if tool_calls:
                history[-1]["content"] += "".join(
                    format_tool_call((tc.get("name") or "unknown"), (tc.get("args") or {}))
                    for tc in tool_calls
                )
                yield "", history


async def generate_response(message: str,
                            history: List[Dict[str, str]]
):
    """生成 Agent 的响应"""
    if not message:
        yield "", history
        return

    # 清洗上一条 AI 回复中的 html 内容，可以为上下文减负
    # 如果不加工具消息和思维链消息将没有这么多事(`ヮ´ )
    if REMOVE_HTML and len(history) >= 1 and history[-1]["role"] == "assistant":
        html_content = history[-1]["content"][0]['text']
        history[-1]["content"][0]['text'] = get_cleaned_text(html_content)

    # print("=================================")
    # print(history)

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})

    messages = history[:-1]

    agent = await get_agent()

    # 避免 MCP 调用失败引发的退出
    try:
        # 使用优化显示
        async for update in _agent_events_optimize(agent, messages, history):
            yield update
    except Exception as err:
        print(f"发生错误: {err}")
        history[-1]["content"] += error_summary(err)
        yield "", history

    yield "", history


def main():
    """主函数"""
    # 配置网络参数
    # docker 预留操作入口，docker 的 host 一般设置为 0.0.0.0
    parser = argparse.ArgumentParser(description="Gradio Agent APP")
    parser.add_argument("--host", type=str, default="localhost", help="主机地址")
    parser.add_argument("--port", type=int, default=7860, help="端口号")
    args = parser.parse_args()

    app = create_ui(
        llm_func=generate_response,
        tab_name="Gradio APP - WebUI",
        main_title="Gradio Agent APP",
        initial_message=[{"role": "assistant", "content": get_greeting()}]
    )

    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=False,
        theme=theme,
        css=custom_css
    )


if __name__ == "__main__":
    main()
