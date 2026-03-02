"""
文件系统工具
"""

import os

from langchain.tools import tool


@tool
def curr_dir() -> str:
    """返回当前工作目录"""
    return os.getcwd()


@tool
def ls_dir(dirpath: str) -> str:
    """列出目录下的所有文件和子目录"""
    if not dirpath:
        return "目录路径不能为空"
    try:
        return '\n'.join(os.listdir(dirpath))
    except Exception as e:
        return f"列出目录失败: {e}"


@tool
def read_file(filepath: str) -> str:
    """读取文件内容"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"读取失败: {e}"
