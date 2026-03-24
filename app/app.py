"""
一个智能体
"""

from __future__ import annotations

import asyncio
import os
import textwrap
import traceback
import uuid
import argparse
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRequest,
    SummarizationMiddleware,
    TodoListMiddleware,
    dynamic_prompt,
)
from langchain.tools import ToolRuntime, tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from config.mcp_config import get_mcp_dict
from prompts import middleware_todolist, prompt_enhance, subagent_search
from tools.tool_role import role_play
from tools.tool_runtime import ToolSchema
from tools.tool_sci import calculator
from tools.tool_search import dashscope_search
from utils.remove_html import get_cleaned_text
from utils.tool_view import format_tool_call, format_tool_result
from utils.web_ui import create_ui, custom_css, theme

load_dotenv()


# ─────────────────────────────────────────────────────────────────────────────
# 配置层
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LLMConfig:
    """LLM 模型配置"""
    model: str = "qwen3-coder-plus"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    enable_thinking: bool = True
    temperature: Optional[float] = None
    top_p: Optional[float] = None

    # ── 支持的 LLM 提供商 ────────────────────────────────────────────────────
    # DashScope 目前有免费额度，支持以下模型：
    #   kimi-k2-thinking / deepseek-v3.2 / glm-4.7 / qwen3-coder-plus-2025-07-22
    # 如果觉得卡，可以使用付费模型：
    #   qwen3-max / qwen3-max-preview / qwen3-coder-plus
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def from_env(cls, provider: str = "dashscope") -> LLMConfig:
        """从环境变量创建 LLM 配置"""
        if provider == "dashscope":
            return cls(
                model="qwen3-coder-plus",
                base_url=os.getenv("DASHSCOPE_BASE_URL"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                enable_thinking=True,
            )
        if provider == "ark":
            # 字节火山方舟，支持：deepseek-v3-2-251201 / kimi-k2-thinking-251104
            return cls(
                model="deepseek-v3-2-251201",
                base_url=os.getenv("ARK_BASE_URL"),
                api_key=os.getenv("ARK_API_KEY"),
                enable_thinking=False,
            )
        if provider == "ollama":
            # 使用前需要：
            #   ollama pull qwen3:4b
            #   OLLAMA_HOST=0.0.0.0:11435 ollama serve
            return cls(
                model="qwen3:4b",
                base_url="http://127.0.0.1:11435/v1",
                api_key="-",
                enable_thinking=True,
                temperature=0.7,
                top_p=0.9,
            )
        raise ValueError(f"未知的 LLM 提供商：{provider!r}")

    def to_kwargs(self) -> dict:
        """转换为 ChatOpenAI 的构造参数"""
        kwargs: dict = {
            "model": self.model,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "timeout": self.timeout,
        }
        if self.enable_thinking:
            kwargs["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": True}
            }
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        return kwargs


@dataclass
class MCPConfig:
    """MCP 服务配置"""
    # 开启的 MCP 服务名称集合
    enabled: frozenset = field(default_factory=lambda: frozenset({
        "code-execution:stdio",
        # "antv-chart:stdio",
        # "filesystem:stdio",
        # "amap-maps:http",
    }))
    base_path: str = "./"

    def get_active_dict(self) -> dict:
        """获取已启用的 MCP 配置字典"""
        return {
            k: v
            for k, v in get_mcp_dict(self.base_path).items()
            if k in self.enabled
        }


@dataclass
class AppConfig:
    """应用总配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    # 是否清洗历史对话中的 HTML 内容（可减轻上下文负担）
    remove_html: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# 动态提示词
# ─────────────────────────────────────────────────────────────────────────────

@dynamic_prompt
def _main_agent_prompt(_: ModelRequest) -> str:
    """主 Agent 的动态系统提示词"""
    return prompt_enhance.get_system_prompt()


@dynamic_prompt
def _search_subagent_prompt(_: ModelRequest) -> str:
    """搜索子 Agent 的动态系统提示词"""
    return subagent_search.get_system_prompt()


# ─────────────────────────────────────────────────────────────────────────────
# 服务层
# ─────────────────────────────────────────────────────────────────────────────

class AgentService:
    """
    Agent 服务

    负责：
    - LLM 实例的懒加载
    - 搜索子 Agent 的懒加载
    - 主 Agent 的创建与并发安全缓存
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._llm: Optional[ChatOpenAI] = None
        self._search_subagent: Optional[Any] = None
        self._agent: Optional[Any] = None
        self._lock = asyncio.Lock()

    # ── LLM ──────────────────────────────────────────────────────────────────

    @property
    def llm(self) -> ChatOpenAI:
        """获取 LLM 实例（懒加载）"""
        if self._llm is None:
            self._llm = ChatOpenAI(**self._config.llm.to_kwargs())
        return self._llm

    # ── 搜索子 Agent ──────────────────────────────────────────────────────────

    @property
    def search_subagent(self) -> Any:
        """获取搜索子 Agent（懒加载）"""
        if self._search_subagent is None:
            self._search_subagent = create_agent(
                model=self.llm,
                tools=[dashscope_search],
                middleware=[_search_subagent_prompt],
            )
        return self._search_subagent

    def _make_search_brief_tool(self) -> Any:
        """创建 subagent_search_brief 工具"""
        subagent = self.search_subagent  # 提前绑定，避免闭包延迟求值

        @tool("subagent_search_brief", description=subagent_search.get_tool_description())
        async def search_brief(query: str, runtime: ToolRuntime[ToolSchema]) -> str:
            """调用搜索子 Agent，返回摘要后的搜索结果"""
            result = await subagent.ainvoke(
                {"messages": [{"role": "user", "content": query}]},
                config={"configurable": {"thread_id": str(uuid.uuid4())}},
                context=runtime.context,
            )
            return result["messages"][-1].content

        return search_brief

    # ── 主 Agent ──────────────────────────────────────────────────────────────

    async def get_agent(self) -> Any:
        """获取主 Agent（懒加载 + 双重检查，并发安全）"""
        if self._agent is not None:
            return self._agent

        async with self._lock:
            if self._agent is not None:  # 双重检查
                return self._agent

            # 获取 MCP 工具
            mcp_dict = self._config.mcp.get_active_dict()
            mcp_tools: List[Any] = []
            if mcp_dict:
                client = MultiServerMCPClient(mcp_dict)
                mcp_tools = await client.get_tools()

            # 本地工具
            local_tools = [
                calculator,
                role_play,
                dashscope_search,
                self._make_search_brief_tool(),
            ]

            self._agent = create_agent(
                model=self.llm,
                tools=mcp_tools + local_tools,
                middleware=[
                    _main_agent_prompt,
                    SummarizationMiddleware(
                        model=self.llm,
                        trigger=("tokens", 2000),
                        keep=("messages", 7),
                    ),
                    TodoListMiddleware(
                        system_prompt=middleware_todolist.get_system_prompt()
                    ),
                ],
            )

        return self._agent


# ─────────────────────────────────────────────────────────────────────────────
# 应用层辅助函数
# ─────────────────────────────────────────────────────────────────────────────

def _get_tools_info(agent: Any) -> str:
    """获取 Agent 工具列表的可读描述"""
    node = agent.get_graph().nodes["tools"]
    tools = list(node.data.tools_by_name.values())

    if len(tools) < 13:
        lines = [
            f"- `{t.name}`: {(t.description or '').split(chr(10))[0]}"
            for t in tools
        ]
        return "\n".join(lines)

    # 工具较多时只展示名称
    wrapped = textwrap.fill(" / ".join(t.name for t in tools), width=100)
    return f"\n```text\n{wrapped}\n```\n"


def _get_greeting(service: AgentService) -> str:
    """获取初始欢迎消息"""
    try:
        agent = asyncio.run(service.get_agent())
        tools_info = _get_tools_info(agent)
        return "\n".join([
            "你好！我是你的智能助手，可以使用的工具包括：",
            tools_info,
            "\n请问有什么可以帮你的吗？",
        ])
    except Exception as exc:
        print(f"获取工具列表时出错: {exc}")
        return "你好！我是你的智能助手。\n请问有什么可以帮你的吗？"


def _summarize_error(llm: ChatOpenAI, err: Exception, limit: int = 500) -> str:
    """用 LLM 总结错误，失败时降级输出原始日志"""
    full_trace = "".join(traceback.format_exception(type(err), err, err.__traceback__))
    full_trace = full_trace[-5000:]  # 避免过长

    try:
        abstract = llm.invoke("\n".join([
            full_trace,
            "---",
            "以上是 LangChain Agent 的报错信息，请简述报错原因：",
        ]))
        return f"\n ⚠️ 发生错误，以下是摘要信息：\n{abstract}"
    except Exception:
        return f"\n ⚠️ 发生错误，以下是原始日志：\n{full_trace[:limit]}"


async def _stream_events(
    agent: Any,
    messages: List[Dict],
    history: List[Dict[str, str]],
    tool_context: ToolSchema,
) -> AsyncIterator[Tuple[str, List[Dict[str, str]]]]:
    """处理 Agent 事件流，更新 history 并逐步 yield"""
    # 需要跳过输出的子 Agent 名称（避免与主流输出重复）
    SKIP_SUBAGENTS = {"subagent:search-brief"}

    async for mode, payload in agent.astream(
        {"messages": messages},
        stream_mode=["messages", "values"],
        context=tool_context,
    ):
        if mode == "messages":
            token, metadata = payload
            node = metadata.get("langgraph_node", "")

            if node == "model" and token.content:
                history[-1]["content"] += token.content
                yield "", history

            elif node == "tools":
                if token.name in SKIP_SUBAGENTS:
                    continue
                if token.content:
                    history[-1]["content"] += format_tool_result(token.name, token.content)
                    yield "", history

        elif mode == "values":
            state_msgs = payload.get("messages") if isinstance(payload, dict) else None
            if not state_msgs:
                continue
            tool_calls = getattr(state_msgs[-1], "tool_calls", None)
            if tool_calls:
                history[-1]["content"] += "".join(
                    format_tool_call(tc.get("name") or "unknown", tc.get("args") or {})
                    for tc in tool_calls
                )
                yield "", history


# ─────────────────────────────────────────────────────────────────────────────
# 应用层：响应生成
# ─────────────────────────────────────────────────────────────────────────────

def make_generate_response(service: AgentService, config: AppConfig):
    """
    工厂函数：返回绑定了 service 和 config 的 generate_response 协程生成器。
    Gradio 的 llm_func 签名为 (message, history) -> AsyncIterator。
    """
    async def generate_response(
        message: str,
        history: List[Dict[str, str]],
    ) -> AsyncIterator[Tuple[str, List[Dict[str, str]]]]:
        if not message:
            yield "", history
            return

        # 清洗上一条 AI 回复中的 HTML（可减轻上下文负担）
        if (
            config.remove_html
            and history
            and history[-1]["role"] == "assistant"
            and isinstance(history[-1].get("content"), list)
        ):
            item = history[-1]["content"][0]
            if isinstance(item, dict) and "text" in item:
                item["text"] = get_cleaned_text(item["text"])

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": ""})

        messages = history[:-1]
        agent = await service.get_agent()
        tool_context = ToolSchema(
            base_url=config.llm.base_url or "",
            api_key=config.llm.api_key or "",
        )

        try:
            async for update in _stream_events(agent, messages, history, tool_context):
                yield update
        except Exception as err:
            print(f"发生错误: {err}")
            history[-1]["content"] += _summarize_error(service.llm, err)
            yield "", history

        yield "", history

    return generate_response


# ─────────────────────────────────────────────────────────────────────────────
# 主函数
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Gradio Agent APP")
    parser.add_argument("--host", default="localhost", help="主机地址")
    parser.add_argument("--port", type=int, default=7860, help="端口号")
    parser.add_argument(
        "--provider",
        default="dashscope",
        choices=["dashscope", "ark", "ollama"],
        help="LLM 提供商",
    )
    args = parser.parse_args()

    config = AppConfig(
        llm=LLMConfig.from_env(args.provider),
        mcp=MCPConfig(),
    )
    service = AgentService(config)

    app = create_ui(
        llm_func=make_generate_response(service, config),
        tab_name="Gradio APP - WebUI",
        main_title="Gradio Agent APP",
        initial_message=[{"role": "assistant", "content": _get_greeting(service)}],
    )
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=False,
        theme=theme,
        css=custom_css,
    )


if __name__ == "__main__":
    main()
