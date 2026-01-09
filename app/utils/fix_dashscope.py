# -*- coding: utf-8 -*-

"""
当前 ChatOpenAI 无法正确解析 DashScope API 中思维链 (thinking) 的内容
本模块通过重写 _astream 方法，将 DashScope 的 reasoning_content 字段解析出来
"""

from typing import Any, AsyncIterator, List, Optional
from langchain_core.callbacks import AsyncCallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk
from langchain_openai import ChatOpenAI

class DashScopeChatOpenAI(ChatOpenAI):

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        # Use _get_request_payload to get all parameters including messages
        params = self._get_request_payload(messages, stop=stop, **kwargs)
        params["stream"] = True

        # self.async_client is already the AsyncCompletions resource
        response = await self.async_client.create(**params)

        async for chunk in response:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            content_text = delta.content or ""
            reasoning_text = getattr(delta, "reasoning_content", None) or ""

            assert not (content_text and reasoning_text), "Content and reasoning cannot be present at the same time"

            final_text = ""
            text_type = ""
            if reasoning_text:
                final_text = reasoning_text
                text_type = "reasoning"
            if content_text:
                final_text = content_text
                text_type = "content"

            additional_kwargs = delta.model_dump()

            msg_chunk = AIMessageChunk(
                content=final_text,
                additional_kwargs=additional_kwargs,
                response_metadata={
                    "dashscope_type": text_type,
                    "finish_reason": choice.finish_reason,
                    "model_name": chunk.model
                }
            )

            generation_chunk = ChatGenerationChunk(message=msg_chunk)
            yield generation_chunk

            if run_manager:
                await run_manager.on_llm_new_token(
                    final_text,
                    chunk=msg_chunk
                )
