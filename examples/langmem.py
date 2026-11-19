"""
langmem 记忆示例
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool
from langchain.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
)

# 创建具有记忆功能的智能体
memory_store = InMemoryStore()

agent = create_agent(
    model=llm,
    tools=[
        # 用于创建、更新、删除记忆的工具
        create_manage_memory_tool(store=memory_store, namespace=("memories",)),
        # 用于搜索现有记忆的工具
        create_search_memory_tool(store=memory_store, namespace=("memories",)),
    ],
)

# 执行示例：使用智能体进行简单对话
response = agent.invoke({"messages": [HumanMessage(content="请记住我喜欢编程。")]})
print("智能体响应:", response["messages"][-1].content)

# 检索记忆以验证存储
search_result = agent.invoke({"messages": [HumanMessage(content="回忆一下我喜欢什么吗？")]})
print("记忆检索结果:", search_result["messages"][-1].content)
