# -*- coding: utf-8 -*-
import asyncio
import os

from . import server


host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", 8001))


def stdio():
    """Stdio entry point for the package."""
    asyncio.run(server.mcp.run(transport="stdio"))


def http():
    """streamable-http entry point for the package."""
    asyncio.run(server.mcp.run(transport="http", host=host, port=port, path="/mcp"))


if __name__ == "__main__":
    http()
