from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tools import tool_role
from tools.tool_role import BestResponse, Response, _select_best_response_record


class _FakeStructuredOutput:
    def __init__(self, llm, schema):
        self.llm = llm
        self.schema = schema

    def invoke(self, prompt):
        if self.schema is Response:
            role = prompt.split("作为一个", 1)[1].split("，", 1)[0]
            return Response(response=f"{role}-reply")

        if self.schema is BestResponse:
            self.llm.best_response_prompt = prompt
            return BestResponse(id=1)

        raise AssertionError(f"unexpected schema: {self.schema}")


class _FakeLLM:
    def __init__(self):
        self.best_response_prompt = ""
        self.structured_output_methods = []

    def with_structured_output(self, schema, **kwargs):
        self.structured_output_methods.append(kwargs.get("method"))
        return _FakeStructuredOutput(self, schema)


class RolePlayTests(unittest.TestCase):
    def test_select_best_response_rejects_negative_id(self):
        responses = [{"role": "A", "content": "alpha"}]

        with self.assertRaisesRegex(ValueError, "无效的最佳回复 ID"):
            _select_best_response_record(responses, BestResponse(id=-1))

    def test_select_best_response_rejects_out_of_range_id(self):
        responses = [{"role": "A", "content": "alpha"}]

        with self.assertRaisesRegex(ValueError, "无效的最佳回复 ID"):
            _select_best_response_record(responses, BestResponse(id=1))

    def test_select_best_response_accepts_valid_id(self):
        responses = [
            {"role": "A", "content": "alpha"},
            {"role": "B", "content": "beta"},
        ]

        self.assertEqual(
            _select_best_response_record(responses, BestResponse(id=1)),
            {"role": "B", "content": "beta"},
        )

    def test_role_play_uses_runtime_model(self):
        graph = Mock()
        graph.invoke.return_value = {
            "responses": [{"role": "A", "content": "alpha"}],
            "best_role": "A",
            "best_response": "alpha",
        }
        runtime = SimpleNamespace(
            context=SimpleNamespace(
                base_url="https://example.test/v1",
                api_key="test-key",
                model="deepseek-v3-2-251201",
            )
        )

        with (
            patch.object(tool_role, "init_chat_model", return_value=Mock()) as init_chat_model,
            patch.object(tool_role, "create_doge_graph", return_value=graph),
        ):
            result = tool_role.role_play.func(runtime=runtime, situation="测试", roles=["A"])

        init_chat_model.assert_called_once_with(
            model="deepseek-v3-2-251201",
            model_provider="openai",
            base_url="https://example.test/v1",
            api_key="test-key",
        )
        self.assertIn("deepseek-v3-2-251201", result)

    def test_role_play_rejects_empty_roles(self):
        runtime = SimpleNamespace(
            context=SimpleNamespace(
                base_url="https://example.test/v1",
                api_key="test-key",
                model="deepseek-v3-2-251201",
            )
        )

        with self.assertRaisesRegex(ValueError, "roles 不能为空"):
            tool_role.role_play.func(runtime=runtime, situation="测试", roles=[])

    def test_role_play_rejects_too_many_roles(self):
        graph = Mock()
        graph.invoke.return_value = {
            "responses": [{"role": "A", "content": "alpha"}],
            "best_role": "A",
            "best_response": "alpha",
        }
        runtime = SimpleNamespace(
            context=SimpleNamespace(
                base_url="https://example.test/v1",
                api_key="test-key",
                model="deepseek-v3-2-251201",
            )
        )

        with (
            patch.object(tool_role, "init_chat_model", return_value=Mock()),
            patch.object(tool_role, "create_doge_graph", return_value=graph),
            self.assertRaisesRegex(ValueError, "roles 最多支持 10 个"),
        ):
            tool_role.role_play.func(
                runtime=runtime,
                situation="测试",
                roles=[f"R{i}" for i in range(11)],
            )

    def test_best_response_prompt_numbers_candidates(self):
        llm = _FakeLLM()
        graph = tool_role.create_doge_graph(llm)

        graph.invoke({"roles": ["A", "B"], "situation": "测试"})

        self.assertIn("0. 【A】A-reply", llm.best_response_prompt)
        self.assertIn("1. 【B】B-reply", llm.best_response_prompt)

    def test_doge_graph_uses_json_mode_for_structured_output(self):
        llm = _FakeLLM()
        graph = tool_role.create_doge_graph(llm)

        graph.invoke({"roles": ["A", "B"], "situation": "测试"})

        self.assertEqual(llm.structured_output_methods, ["json_mode", "json_mode", "json_mode"])


if __name__ == "__main__":
    unittest.main()
