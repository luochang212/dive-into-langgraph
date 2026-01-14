"""
代码执行 MCP Server
"""

import sys
import subprocess
import tempfile
import textwrap
import os

from fastmcp import FastMCP


# 代码执行工具
mcp = FastMCP("code-execution")


@mcp.tool
def execute_python(code: str) -> str:
    """
    在单独的子进程中执行 Python 代码并返回标准输出或标准错误输出。
    用于数学计算、数据分析和逻辑处理。

    Args:
        code (str): 要执行的 Python 代码。

    Returns:
        str: 代码执行的标准输出或标准错误输出。
    """
    # Normalize indentation (LLMs love extra spaces)
    code = textwrap.dedent(code)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(code)
        file_path = f.name

    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "LANG": "C.UTF-8",
    }

    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=20,         # hard stop
            check=False,        # don't raise
            env=env,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stderr:
            return f"Error:\n{stderr}"

        return stdout if stdout else "Execution finished (no output)"

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out"

    except Exception as e:
        return f"Error: {e}"

    finally:
        os.remove(file_path)


if __name__ == "__main__":
    # # 测试
    # print(execute_python("""
    # import math
    # print(sum([i for i in range(10)]))
    # print(math.pi)
    # """))

    # 启动 MCP Server
    import argparse
    import asyncio

    # 配置网络参数
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 8001))

    parser = argparse.ArgumentParser(description="启动代码执行 MCP Server")
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
