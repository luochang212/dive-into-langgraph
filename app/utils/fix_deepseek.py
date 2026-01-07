"""
DeepSeek 模型返回的 tool_calls 参数通常是 JSON 字符串格式，
本模块自动将其解析为字典对象，以确保兼容下游组件。代码来自 @HKUDS
"""

import json
from typing import Optional
from langchain_openai import ChatOpenAI


class DeepSeekChatOpenAI(ChatOpenAI):
    """
    Custom ChatOpenAI wrapper for DeepSeek API compatibility.
    Handles the case where DeepSeek returns tool_calls.args as JSON strings instead of dicts.
    """

    def _create_message_dicts(self, messages: list, stop: Optional[list] = None) -> list:
        """Override to handle response parsing"""
        message_dicts = super()._create_message_dicts(messages, stop)
        return message_dicts

    def _generate(self, messages: list, stop: Optional[list] = None, **kwargs):
        """Override generation to fix tool_calls format in responses"""
        # Call parent's generate method
        result = super()._generate(messages, stop, **kwargs)

        # Fix tool_calls format in the generated messages
        for generation in result.generations:
            for gen in generation:
                if hasattr(gen, "message") and hasattr(gen.message, "additional_kwargs"):
                    tool_calls = gen.message.additional_kwargs.get("tool_calls")
                    if tool_calls:
                        for tool_call in tool_calls:
                            if "function" in tool_call and "arguments" in tool_call["function"]:
                                args = tool_call["function"]["arguments"]
                                # If arguments is a string, parse it
                                if isinstance(args, str):
                                    try:
                                        tool_call["function"]["arguments"] = json.loads(args)
                                    except json.JSONDecodeError:
                                        pass  # Keep as string if parsing fails

        return result

    async def _agenerate(self, messages: list, stop: Optional[list] = None, **kwargs):
        """Override async generation to fix tool_calls format in responses"""
        # Call parent's async generate method
        result = await super()._agenerate(messages, stop, **kwargs)

        # Fix tool_calls format in the generated messages
        for generation in result.generations:
            for gen in generation:
                if hasattr(gen, "message") and hasattr(gen.message, "additional_kwargs"):
                    tool_calls = gen.message.additional_kwargs.get("tool_calls")
                    if tool_calls:
                        for tool_call in tool_calls:
                            if "function" in tool_call and "arguments" in tool_call["function"]:
                                args = tool_call["function"]["arguments"]
                                # If arguments is a string, parse it
                                if isinstance(args, str):
                                    try:
                                        tool_call["function"]["arguments"] = json.loads(args)
                                    except json.JSONDecodeError:
                                        pass  # Keep as string if parsing fails

        return result
