import unittest

from app import AgentService, AppConfig, LLMConfig, MCPConfig


class NamedTool:
    def __init__(self, name):
        self.name = name


class AgentServiceToolTests(unittest.TestCase):
    def _service_for_provider(self, provider):
        service = AgentService(
            AppConfig(
                llm=LLMConfig.from_env(provider),
                mcp=MCPConfig(enabled=frozenset()),
            )
        )
        service._make_search_brief_tool = lambda: NamedTool("subagent_search_brief")
        return service

    def test_dashscope_provider_registers_dashscope_search_tools(self):
        tool_names = [
            tool.name
            for tool in self._service_for_provider("dashscope")._get_local_tools()
        ]

        self.assertIn("role_play", tool_names)
        self.assertIn("dashscope_search", tool_names)
        self.assertIn("subagent_search_brief", tool_names)

    def test_non_dashscope_providers_still_register_role_play(self):
        for provider in ("ark", "ollama"):
            with self.subTest(provider=provider):
                tool_names = [
                    tool.name
                    for tool in self._service_for_provider(provider)._get_local_tools()
                ]

                self.assertIn("role_play", tool_names)
                self.assertNotIn("dashscope_search", tool_names)
                self.assertNotIn("subagent_search_brief", tool_names)


if __name__ == "__main__":
    unittest.main()
