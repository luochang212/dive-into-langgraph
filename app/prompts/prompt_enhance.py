"""
增强版系统提示词
"""

agent_system_prompt = """
你是一位智能助手，旨在帮助用户解决问题。

你的目标是：
- 理解用户意图并提供准确回答
- 合理使用工具辅助决策和操作
- 充分利用用户信息优化回答

思考标准：
- 利用已知的用户信息来个性化回答
- 根据用户问题的复杂度调整思考深度

以下是用户信息：
{device_info}
""".strip()


def get_system_prompt_enhance() -> str:
    """生成系统提示词"""
    # 延迟导入
    from utils.device_info import get_info

    # 获取设备信息
    info = get_info()

    # 处理操作系统信息
    raw_os = info.get("操作系统 (platform)", "Unknown")
    user_os = "macOS" if raw_os == "Darwin" else raw_os

    info_dict = {
        "当前时间": info.get("当前时间 (now)"),
        "当前时区": info.get("时区 (timezone)"),
        "用户名": info.get("用户名 (username)"),
        "用户系统": user_os,
    }

    # 格式化设备信息字符串
    info_str = "\n".join([f"- {k}: {v}" for k, v in info_dict.items() if v and v != 'Unknown'])

    return agent_system_prompt.format(
        device_info=info_str
    )


if __name__ == "__main__":
    import os
    import sys

    # 将项目根目录添加到 Python 路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(current_dir)
    sys.path.insert(0, app_dir)

    print(get_system_prompt_enhance())
