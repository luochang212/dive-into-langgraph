# -*- coding: utf-8 -*-

"""
获取设备信息
"""

import time
import datetime
import getpass
import platform


def _safe_get(func):
    try:
        return func()
    except Exception:
        return "Unknown"


DYNAMIC_INFO = {
    "当前时间 (now)": lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "UTC时间 (utc_now)": lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
}


dev_info = {
    "时区 (timezone)": _safe_get(lambda: time.tzname[0]),
    "操作系统 (platform)": _safe_get(platform.system),
    "用户名 (username)": _safe_get(getpass.getuser),
    "系统版本 (platform_release)": _safe_get(platform.release),
    "系统详细版本 (platform_version)": _safe_get(platform.version),
    "架构 (architecture)": _safe_get(lambda: " ".join(list(platform.architecture()))),
    "机器类型 (machine)": _safe_get(platform.machine),
    "处理器 (processor)": _safe_get(platform.processor),
}


def get_info(key):
    if key in DYNAMIC_INFO:
        return _safe_get(DYNAMIC_INFO[key])
    return dev_info[key]


if __name__ == "__main__":
    res = get_info("当前时间 (now)")
    print(res)
