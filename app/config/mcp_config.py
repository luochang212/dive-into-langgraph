"""
MCP 配置
"""

import os


def gen_abspath(base_path: str, rel_path: str) -> str:
    abs_dir = os.path.abspath(base_path)
    return os.path.join(abs_dir, rel_path)


def get_mcp_dict(base_path: str = "./") -> dict:
    """获取 MCP 配置"""
    return {
        # 下面标 🌟 的服务建议开启
        # =============== 代码执行 MCP ===============
        # 🌟 stdio
        "code-execution:stdio": {
            "command": "python",
            "args": [gen_abspath(base_path, "mcp/code_execution.py")],
            "transport": "stdio",
        },
        # streamable http
        "code-execution:http": {
            "url": "http://localhost:8001/mcp",
            "transport": "http",
        },
        # =============== 高德地图 MCP ===============
        # 🌟 streamable http
        # 必须先申请高德地图 API_KEY，详见 .env.example
        "amap-maps:http": {
            "url": f"https://mcp.amap.com/mcp?key={os.getenv('AMAP_API_KEY')}",
            "transport": "http",
        },
        # =============== 图表可视化 MCP ===============
        # 🌟 stdio
        "antv-chart:stdio": {
            "command": "npx",
            "args": ["-y", "@antv/mcp-server-chart"],
            "transport": "stdio",
        },
        # streamable http
        # 必须先启动服务，参考 mcp/mcp-server-chart/README.md
        "antv-chart:http": {
            "url": "http://localhost:1123/mcp",
            "transport": "http",
        },
        # =============== 文件系统 MCP ===============
        # 🌟 stdio
        "filesystem:stdio": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                gen_abspath(base_path, "space"),
            ],
            "transport": "stdio",
        },
    }
