"""
基础版系统提示词
"""

agent_system_prompt = """
你是一位智能助手，旨在帮助用户解决问题。

你的目标是：
- 理解用户的意图并提供准确的回答
- 利用可用的工具来辅助决策和操作
""".strip()


def get_system_prompt_base() -> str:
    """生成系统提示词"""
    return agent_system_prompt


if __name__ == "__main__":
    print(get_system_prompt_base())
