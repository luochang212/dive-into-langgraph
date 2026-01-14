"""
增强版系统提示词
"""

agent_system_prompt = """
你是一个智能助手

思考标准：
1. 根据用户问题的复杂程度调整思考深度
2. 以下是系统环境信息：
  - 当前时间：{current_time}
  - 当前时区：{current_timezone}
  - 用户名：{username}
  - 操作系统：{user_os}
""".strip()


def get_system_prompt() -> str:
    """获取系统提示词"""
    # 延迟导入
    from utils.device_info import get_info

    # 处理操作系统信息
    raw_os = get_info("操作系统 (platform)") or "Unknown"
    user_os = "macOS" if raw_os == "Darwin" else raw_os

    return agent_system_prompt.format(
        current_time=get_info("当前时间 (now)"),
        current_timezone=get_info("时区 (timezone)"),
        username=get_info("用户名 (username)"),
        user_os=user_os,
    )


if __name__ == "__main__":
    import os
    import sys

    # 将项目根目录添加到 Python 路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(current_dir)
    sys.path.insert(0, app_dir)

    print(get_system_prompt())
