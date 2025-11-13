"""
使用 RedisStore 存储智能体记忆
参考: https://docs.langchain.com/oss/python/langgraph/add-memory#add-long-term-memory

运行前准备：
    $ pip install -U langgraph-checkpoint-redis
    $ docker compose up -d
    $ docker exec myredis redis-cli ping
运行后查询：
    $ docker exec myredis redis-cli JSON.GET store:01
"""

import os
import uuid

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.store.redis import RedisStore  
from langgraph.store.base import BaseStore

# 加载模型配置
_ = load_dotenv()

# 加载模型
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
    temperature=0.7,
)

DB_URI = "redis://localhost:6379"

with (
    RedisStore.from_conn_string(DB_URI) as store,
):
    store.setup()

    def call_model(
        state: MessagesState,
        config: RunnableConfig,
        *,
        store: BaseStore,  
    ):
        user_id = config["configurable"]["user_id"]
        namespace = ("memories", user_id)
        memories = store.search(namespace, query=str(state["messages"][-1].content))  
        info = "\n".join([d.value["data"] for d in memories])
        system_msg = f"You are a helpful assistant talking to the user. User info: {info}"

        # Store new memories if the user asks the model to remember
        last_message = state["messages"][-1]
        if "remember" in last_message.content.lower():
            memory = "User name is Bob"
            store.put(namespace, str(uuid.uuid4()), {"data": memory})  

        response = llm.invoke(
            [{"role": "system", "content": system_msg}] + state["messages"]
        )
        return {"messages": response}

    builder = StateGraph[MessagesState, None, MessagesState, MessagesState](MessagesState)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")

    graph = builder.compile(
        store=store,  
    )

    config = {
        "configurable": {
            "thread_id": "1",  
            "user_id": "1",  
        }
    }
    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": "Hi! Remember: my name is Bob"}]},
        config,  
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()

    config = {
        "configurable": {
            "thread_id": "2",  
            "user_id": "1",
        }
    }

    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": "what is my name?"}]},
        config,
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()
