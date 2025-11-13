import os
import uuid

from dotenv import load_dotenv
from typing_extensions import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


# 加载模型配置
_ = load_dotenv()


# 加载模型
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
    temperature=0.7,
)


class State(TypedDict):
    topic: NotRequired[str]
    joke: NotRequired[str]


def generate_topic(state: State):
    """调用 LLM 生成一个笑话主题"""
    msg = llm.invoke("请写一个有趣的笑话主题")
    return {"topic": msg.content}


def write_joke(state: State):
    """根据笑话主题，调用 LLM 编写一个简短笑话"""
    msg = llm.invoke(f"请围绕笑话主题「{state['topic']}」写一个简短的笑话")
    return {"joke": msg.content}


# 构建工作流
workflow = StateGraph(State)

# 添加节点
workflow.add_node("generate_topic", generate_topic)
workflow.add_node("write_joke", write_joke)

# 连接节点的边
workflow.add_edge(START, "generate_topic")
workflow.add_edge("generate_topic", "write_joke")
workflow.add_edge("write_joke", END)

# 编译
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

# 执行工作流
config = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}
state = graph.invoke({}, config)

print(state["topic"])
print()
print(state["joke"])

# 状态将按时间倒序返回
states = list(graph.get_state_history(config))

for state in states:
    print(state.next)
    print(state.config["configurable"]["checkpoint_id"])
    print()

# 这是倒数第二个状态（状态按时间顺序列出）
selected_state = states[1]
print(selected_state.next)
print(selected_state.values)

# 创建一个新的检查点，新检查点将与同一线程相关联，但有一个新的检查点 ID
new_config = graph.update_state(selected_state.config, values={"topic": "蘑菇"})
new_config = graph.update_state(new_config, values={"joke": ""})
print(new_config)

# 从检查点恢复执行
new_state = graph.invoke(None, new_config)

print(new_state["topic"])
print()
print(new_state["joke"])

# recalc = write_joke(new_state)
# print(recalc["joke"])
