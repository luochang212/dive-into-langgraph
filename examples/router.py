import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
)

# 1) 定义一个简单工具
def get_weather(city: str) -> str:
    """Return a simple weather string for the given city."""
    return f"It's always sunny in {city}!"

# 2) 创建工具agent节点
tool_agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

def run_tool_agent(state: MessagesState):
    # 透传消息给 agent，返回其消息栈
    res = tool_agent.invoke({"messages": state["messages"]})
    return {"messages": res["messages"]}

# 3) 路由节点：简单规则判断是否需要走工具
def route(state: MessagesState):
    text = state["messages"][-1].content.lower()
    if re.search(r"天气|weather|气温|温度|城市|city", text):
        return "tool"
    return "chat"

graph_builder = StateGraph(MessagesState)

def chatbot(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("router", lambda s: s)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tool_agent", run_tool_agent)

graph_builder.add_conditional_edges(
    "router",
    route,
    {"chat": "chatbot", "tool": "tool_agent"},
)

graph_builder.add_edge(START, "router")
graph_builder.add_edge("chatbot", END)
graph_builder.add_edge("tool_agent", END)
graph = graph_builder.compile()

result = graph.invoke({"messages": [HumanMessage(content="你好，北京是什么天气")]})
print(result["messages"][-1].content)
