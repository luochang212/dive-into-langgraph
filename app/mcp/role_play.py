"""
角色扮演 MCP Server

使用方式：
    export HOST=127.0.0.1
    export PORT=8000
    python role_play.py -t http
"""

import os
import operator

from dotenv import load_dotenv
from typing import Annotated, TypedDict
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from fastmcp import FastMCP

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
env_path = os.path.join(app_dir, '.env')

load_dotenv(dotenv_path=env_path)

# 加载环境变量
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

# 角色扮演的提示词
role_play_prompt = "面对女神{situation}的情况，作为一个{role}，你应该如何一句话回复女神？请以JSON格式返回，包含response字段"

# 最佳回复的提示词
best_response_prompt = """下面是几种类型的男生，面对女神{situation}的情况，做出的反应。
你觉得以下哪种回复最能挽回女神的心，请返回对应的ID。
注意哦，第一条反应对应的是0号ID。请以JSON格式返回，包含id字段
下面是男生们的反应：\n\n{responses}"""

# 角色
class Roles(BaseModel):
    roles: list[str]

# 单个角色
class Role(BaseModel):
    role: str
    situation: str

# 单个回复
class Response(BaseModel):
    response: str

# 最佳回复的 ID
class BestResponse(BaseModel):
    id: int

# 全局上下文
class Overall(TypedDict):
    situation: str
    roles: list[str]
    responses: Annotated[list, operator.add]
    best_response: str
    best_role: str

# 定义 Doge 工作流输出的 Schema
class DogeOutput(TypedDict):
    roles: list[str]
    responses: list[dict]
    best_response: str
    best_role: str

# 创建 Doge 工作流
def create_doge_graph(llm):

    # [MAP] 使用 Send 函数分发角色
    def continue_to_responses(state: Overall):
        return [ Send("generate_response", {"role": r, "situation": state["situation"]}) for r in state["roles"] ]

    # [MAP] 角色回复节点：生成每个角色的回复
    def generate_response(state: Role):
        prompt = role_play_prompt.format(role=state["role"], situation=state["situation"])
        response = llm.with_structured_output(Response).invoke(prompt)
        return {"responses": [{"role": state["role"], "content": response.response}]}

    # [REDUCE] 最佳回复节点：返回最佳回复
    def best_response(state: Overall):
        responses = "\n\n".join([r["content"] for r in state["responses"]])
        prompt = best_response_prompt.format(responses=responses, situation=state["situation"])
        response = llm.with_structured_output(BestResponse).invoke(prompt)
        best_record = state["responses"][response.id]
        return {"best_response": best_record["content"], "best_role": best_record["role"]}

    doge_builder = StateGraph(Overall, output_schema=DogeOutput)

    # 添加节点
    doge_builder.add_node("generate_response", generate_response)
    doge_builder.add_node("best_response", best_response)

    # 添加边
    doge_builder.add_conditional_edges(START, continue_to_responses, ["generate_response"])
    doge_builder.add_edge("generate_response", "best_response")
    doge_builder.add_edge("best_response", END)

    # 编译图
    doge_graph = doge_builder.compile(name='best-response')

    return doge_graph

# 角色扮演工具
mcp = FastMCP("role-play")

@mcp.tool
def role_play(
    situation: str = "告诉你她今天要加班",
    roles: list[str] = [
        "男神", "巨魔", "舔狗", "渣男", "奶狗弟弟", "社恐宅男",
        "霸道总裁", "茶茶的男生", "文艺长发男", "萌萌二次元"
    ],
):
    """在指定情境下，模拟多个人设与女神对话的场景

    比如，你可以将情境设定为 "不回我消息"，然后模拟不同角色（如男神、舔狗、渣男等）对女神的回复。
    最后，模型会根据所有回复，评选出最能挽回女神的心的回复。

    该工具使用指定的 LLM 模型，模拟多种不同人设（如男神、舔狗、渣男等）在特定情境下的回复，
    并由模型评选出最合适的回复。当人设数量 ≤ 20 时，建议向用户返回全部人设的结果。

    Args:
        situation: 设定的情境描述，默认为 "告诉你她今天要加班"
        roles: 参与角色扮演的人设列表，默认为一组预设的典型角色

    Returns:
        str: 包含所有角色回复及最佳回复评选结果的格式化文本
    """
    # 默认使用 qwen3-max
    model_name = "qwen3-max"
    llm = init_chat_model(
        model=model_name,
        model_provider="openai",
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
    )
    doge_graph = create_doge_graph(llm)
    response = doge_graph.invoke({"roles": roles, "situation": situation})

    return "\n".join(
        [f"{len(roles)} 种人设的回复："]
        + [f"\n【{item['role']}】\n{item['content']}" for item in response["responses"]]
        + [f"\n最受 {model_name} 喜爱的是【{response.get('best_role')}】的回复：\n{response['best_response']}"]
    )


if __name__ == "__main__":
    # # 测试
    # print(role_play.fn())

    # 启动 MCP Server
    import argparse
    import asyncio

    # 配置网络参数
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 8000))

    parser = argparse.ArgumentParser(description="启动角色扮演 MCP Server")
    parser.add_argument("-t", "--transport", type=str, default="stdio", help="通信方式，可选 stdio 或 http")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "http":
        asyncio.run(mcp.run(transport="http",
                            host=host,
                            port=port,
                            path="/mcp"))
    else:
        raise ValueError(f"Unknown transport: {args.transport}")
