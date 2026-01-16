"""
子智能体-搜索系统提示词
"""

from datetime import datetime


agent_system_prompt = """
你是一个负责网络搜索的子智能体，接受上层智能体的调用。
你将返回搜索结果的摘要，摘要长度需要控制在两百个词以内。

注意事项：
- 避免在搜索中泄漏用户个人隐私或敏感信息
- 当用户问题有语法错误或表意不清时，请对用户问题进行改写
- 不要在搜索结果中加入自己的理解
- 当前时间是：{current_time}
""".strip()


tool_description = """
一个拥有独立上下文空间的 subagent，支持联网搜索，返回摘要后的搜索结果

注意，它不返回完整的搜索结果，只返回搜索结果的摘要。请确认这符合你的使用场景

建议使用场景：
1. 需要节约上下文，不希望收到详细的搜索结果
2. 预计搜索结果不复杂，可以被简要描述

注意事项：
1. 每次只执行一个查询。如有多个查询，分多次执行
2. 请简短但完整地告诉它上下文信息（如有）

例如：搜索圣何塞的经纬度、海拔高度
""".strip()


def get_system_prompt() -> str:
    """获取系统提示词"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return agent_system_prompt.format(
        current_time=current_time,
    )


def get_tool_description() -> str:
    """获取工具描述"""
    return tool_description


if __name__ == "__main__":
    print(get_system_prompt())
    print("=" * 45)
    print(get_tool_description())
