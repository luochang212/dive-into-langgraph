import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# 加载模型配置
load_dotenv()

# 配置大模型服务
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
)

# 创建Agent
agent = create_agent(model=llm)

# langgraph-cli 入口函数
def get_app():
    return agent
