import asyncio
import unittest
from unittest.mock import patch

import app as app_module
from app import AppConfig, LLMConfig, make_generate_response
from tools.tool_runtime import ToolSchema
from utils.tool_view import format_tool_call, format_tool_result


class ServiceThatShouldNotStart:
    llm = None

    async def get_agent(self):
        raise AssertionError("agent should not start before the first UI update")


class ServiceThatRecordsStartup:
    llm = None

    def __init__(self):
        self.started = False

    async def get_agent(self):
        self.started = True
        raise AssertionError("agent should not start before the first UI update")


class StaticAgentService:
    llm = None

    async def get_agent(self):
        return object()


class FailingAgentService:
    llm = None

    async def get_agent(self):
        raise RuntimeError("agent init failed")


class AsyncSummaryLLM:
    def invoke(self, prompt):
        raise AssertionError("sync invoke should not be called from async response path")

    async def ainvoke(self, prompt):
        return "async summary"


class V2StreamingAgent:
    def __init__(self):
        self.kwargs = None

    async def astream(self, inputs, **kwargs):
        self.kwargs = kwargs
        yield {
            "type": "messages",
            "ns": (),
            "data": (
                type("Token", (), {"content": "hello", "name": None})(),
                {"langgraph_node": "model"},
            ),
        }
        yield {
            "type": "values",
            "ns": (),
            "data": {"messages": [type("Message", (), {"tool_calls": []})()]},
        }


class ScriptedV2Agent:
    """按给定脚本顺序回放 v2 流式事件的 mock agent"""

    def __init__(self, parts):
        self.parts = parts

    async def astream(self, inputs, **kwargs):
        for part in self.parts:
            yield part


def _reasoning_token(text):
    """模拟 qwen 混合思考模型的思考增量（reasoning_content 在 additional_kwargs 中）"""
    return type(
        "Token",
        (),
        {"content": "", "name": None, "additional_kwargs": {"reasoning_content": text}},
    )()


def _content_token(text):
    return type(
        "Token",
        (),
        {"content": text, "name": None, "additional_kwargs": {}},
    )()


class GenerateResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_events_uses_v2_envelope(self):
        agent = V2StreamingAgent()
        history = [{"role": "assistant", "content": app_module.TYPING_INDICATOR_HTML}]

        updates = [
            update
            async for update in app_module._stream_events(
                agent,
                [{"role": "user", "content": "hello"}],
                history,
                ToolSchema(base_url="", api_key="", model="test"),
            )
        ]

        self.assertEqual(agent.kwargs["version"], "v2")
        self.assertEqual(agent.kwargs["stream_mode"], ["messages", "values"])
        self.assertEqual(history[-1]["content"], "hello")
        self.assertEqual(updates[-1], ("", history))

    async def _stream_script(self, parts, history):
        agent = ScriptedV2Agent(parts)
        return [
            update
            async for update in app_module._stream_events(
                agent,
                [{"role": "user", "content": "hi"}],
                history,
                ToolSchema(base_url="", api_key="", model="test"),
            )
        ]

    async def test_stream_events_renders_reasoning_as_collapsible_block(self):
        history = [{"role": "assistant", "content": app_module.TYPING_INDICATOR_HTML}]
        parts = [
            {
                "type": "messages",
                "ns": (),
                "data": (_reasoning_token("先想想"), {"langgraph_node": "model"}),
            },
            {
                "type": "messages",
                "ns": (),
                "data": (_reasoning_token("再验证"), {"langgraph_node": "model"}),
            },
            {
                "type": "messages",
                "ns": (),
                "data": (_content_token("这是答案"), {"langgraph_node": "model"}),
            },
        ]

        await self._stream_script(parts, history)

        final = history[-1]["content"]
        # 思考块存在、多段思考增量聚在同一块内、默认折叠
        self.assertIn('<details class="think-result-details">', final)
        self.assertIn("先想想再验证", final)
        # 正文出现在思考块之后，typing indicator 已清除
        self.assertLess(final.index("</details>"), final.index("这是答案"))
        self.assertNotIn(app_module.TYPING_INDICATOR_HTML, final)

    async def test_stream_events_tool_block_survives_later_reasoning(self):
        history = [{"role": "assistant", "content": app_module.TYPING_INDICATOR_HTML}]
        parts = [
            {
                "type": "messages",
                "ns": (),
                "data": (_reasoning_token("第一段思考"), {"langgraph_node": "model"}),
            },
            {
                "type": "values",
                "ns": (),
                "data": {
                    "messages": [
                        type(
                            "Message",
                            (),
                            {"tool_calls": [{"name": "calculator", "args": {"a": 1}}]},
                        )()
                    ]
                },
            },
            {
                "type": "messages",
                "ns": (),
                "data": (_content_token("中间正文"), {"langgraph_node": "model"}),
            },
            {
                "type": "messages",
                "ns": (),
                "data": (_reasoning_token("第二段思考"), {"langgraph_node": "model"}),
            },
            {
                "type": "messages",
                "ns": (),
                "data": (_content_token("结尾"), {"langgraph_node": "model"}),
            },
        ]

        await self._stream_script(parts, history)

        final = history[-1]["content"]
        # 顺序：思考块1 → 工具调用块 → 正文 → 思考块2 → 结尾
        # 第二段思考必须开新块，且不能把工具块切掉
        self.assertIn("tool-call-details", final)
        self.assertEqual(
            [
                final.index("第一段思考"),
                final.index("tool-call-details"),
                final.index("中间正文"),
                final.index("第二段思考"),
                final.index("结尾"),
            ],
            sorted(
                [
                    final.index("第一段思考"),
                    final.index("tool-call-details"),
                    final.index("中间正文"),
                    final.index("第二段思考"),
                    final.index("结尾"),
                ]
            ),
        )
        self.assertEqual(final.count('<details class="think-result-details">'), 2)

    def test_build_llm_messages_cleans_assistant_tool_html(self):
        tool_html = (
            "before\n"
            + format_tool_call("calculator", {"expression": "1+1"})
            + "between\n"
            + format_tool_result("calculator", "2")
            + "after"
        )
        history = [
            {"role": "user", "content": "please calculate"},
            {"role": "assistant", "content": tool_html},
        ]

        messages = app_module.build_llm_messages(history)

        self.assertEqual(history[1]["content"], tool_html)
        self.assertEqual(messages[0], {"role": "user", "content": "please calculate"})
        self.assertNotIn("<details", messages[1]["content"])
        self.assertNotIn("<summary", messages[1]["content"])
        self.assertNotIn("<svg", messages[1]["content"])
        self.assertIn('```tool_call name="calculator"', messages[1]["content"])
        self.assertIn('```tool_return name="calculator"', messages[1]["content"])
        self.assertIn("before", messages[1]["content"])
        self.assertIn("after", messages[1]["content"])

    def test_build_llm_messages_does_not_clean_user_html_like_text(self):
        user_content = '<details class="tool-result-details"><pre>keep me</pre></details>'
        history = [{"role": "user", "content": user_content}]

        messages = app_module.build_llm_messages(history)

        self.assertEqual(messages, [{"role": "user", "content": user_content}])
        self.assertIsNot(messages, history)

    async def test_whitespace_only_message_is_ignored(self):
        history = []
        generate_response = make_generate_response(
            ServiceThatShouldNotStart(),
            AppConfig(),
        )

        response = generate_response("   ", history)
        message, updated_history = await anext(response)
        await response.aclose()

        self.assertEqual(message, "")
        self.assertEqual(updated_history, [])
        self.assertEqual(history, [])

    async def test_summarize_error_uses_async_llm_call(self):
        summary = await app_module._summarize_error(
            AsyncSummaryLLM(),
            RuntimeError("agent init failed"),
        )

        self.assertIn("async summary", summary)

    async def test_user_message_and_typing_indicator_are_yielded_before_agent_startup(self):
        history = []
        service = ServiceThatRecordsStartup()
        generate_response = make_generate_response(service, AppConfig())

        response = generate_response("hello", history)
        message, updated_history = await anext(response)
        await response.aclose()

        self.assertEqual(message, "")
        self.assertIs(updated_history, history)
        self.assertFalse(service.started)
        self.assertEqual(history[0], {"role": "user", "content": "hello"})
        self.assertEqual(history[1]["role"], "assistant")
        self.assertIn("typing-indicator", history[1]["content"])

    async def test_tool_context_uses_configured_model(self):
        captured = {}

        async def stream_events(agent, messages, history, tool_context):
            captured["tool_context"] = tool_context
            yield "", history

        generate_response = make_generate_response(
            StaticAgentService(),
            AppConfig(
                llm=LLMConfig(
                    model="deepseek-v3-2-251201",
                    base_url="https://example.test/v1",
                    api_key="test-key",
                )
            ),
        )

        with patch("app._stream_events", stream_events):
            async for _ in generate_response("hello", []):
                pass

        self.assertEqual(captured["tool_context"].model, "deepseek-v3-2-251201")

    async def test_agent_startup_error_is_rendered_in_history(self):
        history = []
        generate_response = make_generate_response(
            FailingAgentService(),
            AppConfig(),
        )

        with patch("builtins.print"):
            response = generate_response("hello", history)
            message, updated_history = await anext(response)
            self.assertEqual(message, "")
            self.assertIs(updated_history, history)
            self.assertEqual(history[0], {"role": "user", "content": "hello"})
            self.assertEqual(history[1]["role"], "assistant")
            self.assertIn("typing-indicator", history[1]["content"])

            message, updated_history = await anext(response)
            await response.aclose()

        self.assertEqual(message, "")
        self.assertIs(updated_history, history)
        self.assertEqual(history[0], {"role": "user", "content": "hello"})
        self.assertEqual(history[1]["role"], "assistant")
        self.assertNotIn("typing-indicator", history[1]["content"])
        self.assertIn("agent init failed", history[1]["content"])

    async def test_generation_cancellation_clears_typing_indicator_and_reraises(self):
        history = []
        generate_response = make_generate_response(
            StaticAgentService(),
            AppConfig(),
        )

        async def stream_events(agent, messages, history, tool_context):
            raise asyncio.CancelledError()
            yield "", history

        with patch("app._stream_events", stream_events):
            response = generate_response("hello", history)
            message, updated_history = await anext(response)
            self.assertEqual(message, "")
            self.assertIs(updated_history, history)
            self.assertIn("typing-indicator", history[1]["content"])

            with self.assertRaises(asyncio.CancelledError):
                await anext(response)
            await response.aclose()

        self.assertEqual(history[1]["content"], "")

    async def test_generate_response_sends_cleaned_history_to_agent_without_mutating_ui_history(
        self,
    ):
        captured = {}
        tool_html = format_tool_result("calculator", "2")
        history = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": tool_html},
        ]

        async def stream_events(agent, messages, history, tool_context):
            captured["messages"] = messages
            captured["ui_history"] = history
            yield "", history

        generate_response = make_generate_response(
            StaticAgentService(),
            AppConfig(),
        )

        with patch("app._stream_events", stream_events):
            async for _ in generate_response("next", history):
                pass

        self.assertIn("<details", history[1]["content"])
        self.assertNotIn("<details", captured["messages"][1]["content"])
        self.assertIn('```tool_return name="calculator"', captured["messages"][1]["content"])
        self.assertEqual(captured["messages"][-1], {"role": "user", "content": "next"})
        self.assertIs(captured["ui_history"], history)


if __name__ == "__main__":
    unittest.main()
