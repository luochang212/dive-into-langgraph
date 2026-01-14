"""
基础版系统提示词
"""

agent_system_prompt = "You are a helpful assistant. Be concise and accurate."


def get_system_prompt() -> str:
    """获取系统提示词"""
    return agent_system_prompt


if __name__ == "__main__":
    print(get_system_prompt())
