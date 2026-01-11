"""
流式输出
"""

import os
import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv("../.env")

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

agent = create_agent(
    model=llm,
)

async def run_agent(some_input: dict, config: dict):
    async for chunk in agent.astream(some_input, config):
        print(chunk)
asyncio.run(run_agent({"messages": [{"role": "user","content": "你好"}]}, {}))
