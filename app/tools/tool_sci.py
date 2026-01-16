"""
科学计算工具
"""

import ast
import math
import operator

from langchain.tools import tool


class SafeEvaluator(ast.NodeVisitor):

    # 支持的二元运算
    BIN_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }

    # 支持的一元运算
    UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    # 支持的函数
    SAFE_FUNCS = {
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "log2": math.log2,
        "log10": math.log10,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
    }

    def visit(self, node):
        return super().visit(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Name(self, node):
        # 明确禁止变量名
        raise ValueError(f"不支持变量: {node.id}")

    def visit_BinOp(self, node):
        # 检查二元运算符
        op_type = type(node.op)
        if op_type not in self.BIN_OPS:
            raise ValueError(f"不支持的二元运算符: {op_type}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self.BIN_OPS[op_type](left, right)

    def visit_UnaryOp(self, node):
        # 检查一元运算符
        op_type = type(node.op)
        if op_type not in self.UNARY_OPS:
            raise ValueError(f"不支持的一元运算符: {op_type}")
        operand = self.visit(node.operand)
        return self.UNARY_OPS[op_type](operand)

    def visit_Call(self, node):
        # 检查函数调用
        if not isinstance(node.func, ast.Name):
            raise ValueError("函数调用格式错误")

        func_name = node.func.id
        if func_name not in self.SAFE_FUNCS:
            raise ValueError(f"不支持的函数: {func_name}")

        if len(node.args) != 1:
            raise ValueError(f"{func_name} 函数需要且仅需要一个参数")

        arg = self.visit(node.args[0])
        return self.SAFE_FUNCS[func_name](arg)

    def visit_Constant(self, node):
        if not isinstance(node.value, (int, float)):
            raise ValueError(f"只支持整数或浮点数，不支持 {type(node.value).__name__}")
        return node.value

    def generic_visit(self, node):
        # 一切未列入白名单的节点，直接拒绝
        raise ValueError(f"不支持的语法: {type(node).__name__}")

    def evaluate(self, expression: str) -> float | int:
        # 安全计算数学表达式
        if not expression.strip():
            raise ValueError("表达式不能为空")

        try:
            tree = ast.parse(expression, mode="eval")
            result = self.visit(tree)

            if isinstance(result, (int, float)):
                return result
            else:
                raise ValueError(f"计算结果类型错误: {type(result)}")
        except ZeroDivisionError:
            raise ValueError("除零错误")
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"无效的数学表达式: {str(e)}")


@tool()
def calculator(expression: str) -> str:
    """
    安全计算数学表达式

    支持的运算符: + - * / ** ()
    支持的函数: sqrt exp log log2 log10 sin cos tan abs

    注意: 上叙函数仅支持单参数。像 log(9, 3) 这样的，不行
    例子: 计算 (sqrt(9) + 1) ** 2
    """
    evaluator = SafeEvaluator()
    result = evaluator.evaluate(expression)
    return str(result)
