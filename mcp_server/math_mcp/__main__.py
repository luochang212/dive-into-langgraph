# -*- coding: utf-8 -*-
import os

from . import server


host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", 8001))


def stdio():
    """Stdio entry point for the package."""
    # 注意: fastmcp 4.x 的 run() 是同步函数（内部自带事件循环），不要用 asyncio.run 包裹
    server.mcp.run(transport="stdio")


def http():
    """streamable-http entry point for the package."""
    server.mcp.run(transport="http", host=host, port=port, path="/mcp")


if __name__ == "__main__":
    http()
