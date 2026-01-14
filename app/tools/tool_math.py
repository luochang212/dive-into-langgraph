"""
数学计算工具
"""

from langchain.tools import tool


@tool()
def add(a: float, b: float) -> float:
    """两数相加 (支持整数和浮点数)"""
    return float(a) + float(b)


@tool()
def subtract(a: float, b: float) -> float:
    """两数相减 (支持整数和浮点数)"""
    return float(a) - float(b)


@tool()
def multiply(a: float, b: float) -> float:
    """两数相乘 (支持整数和浮点数)"""
    return float(a) * float(b)


@tool()
def divide(a: float, b: float) -> float:
    """两数相除 (支持整数和浮点数)"""
    if float(b) == 0:
        return "Error: Division by zero"
    return float(a) / float(b)
