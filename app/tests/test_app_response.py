import asyncio
import unittest
from unittest.mock import patch

import app as app_module
from app import AppConfig, LLMConfig, make_generate_response
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


class GenerateResponseTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_generate_response_sends_cleaned_history_to_agent_without_mutating_ui_history(self):
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
