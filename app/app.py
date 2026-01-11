"""
一个智能体
"""

import os
import asyncio
import textwrap
import argparse

from typing import List, Dict, AsyncIterator, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware, dynamic_prompt, ModelRequest
from utils.web_ui import create_ui, theme, custom_css
from utils.tool_view import format_tool_call, format_tool_result
from utils.remove_html import get_cleaned_text
from tools.tool_math import add, subtract, multiply, divide
from tools.tool_search import dashscope_search, SearchTool
from prompts.prompt_base import get_system_prompt_base
from prompts.prompt_enhance import get_system_prompt_enhance


# 加载模型配置
# 注意‼️：请先在 .env 中配置 DASHSCOPE_API_KEY
load_dotenv()


# 是否清洗历史对话记录中的 HTML 内容
REMOVE_HTML = False


# 全局变量
_agent = None  # 全局 Agent 实例
_llm = None  # 全局 LLM 实例
_greeting = ""  # 智能体自我介绍


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    return get_system_prompt_enhance()


async def get_agent():
    """获取全局 Agent 实例"""
    global _agent, _llm
    if _agent is None:
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

        _llm = llm

        # 接入 MCP
        client = MultiServerMCPClient(  
            {
                # 下面标 🌟 的服务建议开启
                # =============== 角色扮演 MCP ===============
                # 🌟 stdio
                "role-play": {
                    "command": "python",
                    "args": [os.path.abspath("./mcp/role_play.py")],
                    "transport": "stdio",
                },
                # # streamable http
                # "role-play": {
                #     "url": "http://localhost:8000/mcp",
                #     "transport": "streamable_http",
                # },
                # =============== 代码执行 MCP ===============
                # 🌟 stdio
                "code-execution": {
                    "command": "python",
                    "args": [os.path.abspath("./mcp/code_execution.py")],
                    "transport": "stdio",
                },
                # # streamable http
                # "code-execution": {
                #     "url": "http://localhost:8001/mcp",
                #     "transport": "streamable_http",
                # },
                # =============== 高德地图 MCP ===============
                # 🌟 streamable http
                # 必须先申请高德地图 API_KEY，详见 .env.example
                "高德地图": {
                    "url": f"https://mcp.amap.com/mcp?key={os.getenv('AMAP_API_KEY')}",
                    "transport": "streamable_http",
                },
                # =============== 图表可视化 MCP ===============
                # # 🌟 stdio
                # "图表可视化": {
                #     "command": "npx",
                #     "args": ["-y", "@antv/mcp-server-chart"],
                #     "transport": "stdio",
                # },
                # # streamable http
                # # 必须先启动服务，参考 mcp/mcp-server-chart/README.md
                # "图表可视化": {
                #     "url": "http://localhost:1123/mcp",
                #     "transport": "streamable_http",
                # },
                # =============== 文件系统 MCP ===============
                # # 🌟 stdio
                # "filesystem": {
                #     "command": "npx",
                #     "args": [
                #         "-y",
                #         "@modelcontextprotocol/server-filesystem",
                #         os.path.abspath("./space"),
                #     ],
                #     "transport": "stdio",
                # },
                # =============== The End ===============
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
        _agent = create_agent(
            model=llm,
            tools=mcp_tools + [add, subtract, multiply, divide, dashscope_search, call_subagent],
            system_prompt=get_system_prompt_base(),
            middleware=[
                dynamic_system_prompt,
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
    global _greeting
    if not _greeting:
        try:
            tools_info = get_tools()
            _greeting = "\n".join([
                "你好！我是你的智能助手，可以使用的工具包括：",
                tools_info,
                "\n请问有什么可以帮你的吗？",
            ])
        except Exception as e:
            print(f"获取工具列表时出错: {e}")
            _greeting = "你好！我是你的智能助手。\n请问有什么可以帮你的吗？"
    return _greeting


def err_summary(err: Exception, limit: int = 300) -> str:
    """总结 Agent 运行错误"""
    # 优先输出日志摘要，失败则降级为原始日志
    summary = ""
    try:
        abstract = _llm.invoke("\n".join([
            str(err),
            "---",
            "以上是 LangChain Agent 的报错信息，请简述报错原因：",
        ]))
        summary = f"\n ⚠️ 发生错误，以下是摘要信息：\n{abstract}"
    except Exception:
        summary = f"\n ⚠️ 发生错误，以下是原始日志：\n{str(err)[:limit]}"

    return summary


async def _agent_events(
    agent,
    messages,
    history: List[Dict[str, str]],
) -> AsyncIterator[Tuple[str, List[Dict[str, str]]]]:
    """简化显示，仅处理 messages 事件流"""
    async for token, metadata in agent.astream(
        {"messages": messages},
        stream_mode="messages",
        context=SearchTool(api_key=os.getenv("DASHSCOPE_API_KEY")),
    ):
        if metadata["langgraph_node"] == "model":
            # 模型回复
            if token.content:
                history[-1]["content"] += token.content
                yield "", history
        elif metadata["langgraph_node"] == "tools":
            # 工具调用结果
            if token.content:
                history[-1]["content"] += format_tool_result(token.name, token.content)
                yield "", history


async def _agent_events_optimize(
    agent,
    messages,
    history: List[Dict[str, str]],
) -> AsyncIterator[Tuple[str, List[Dict[str, str]]]]:
    """优化显示，处理 messages 和 values 事件流"""
    async for mode, payload in agent.astream(
        {"messages": messages},
        stream_mode=["messages", "values"],
        context=SearchTool(api_key=os.getenv("DASHSCOPE_API_KEY")),
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
        history[-1]["content"] += err_summary(err)
        yield "", history

    yield "", history


def main():
    """主函数"""
    # 配置网络参数
    # 为 docker 预留的操作入口，因为 docker 的 host 一般设置为 0.0.0.0
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
