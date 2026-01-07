# 图表可视化 MCP 服务器

GitHub: [antvis/mcp-server-chart](https://github.com/antvis/mcp-server-chart)

全局安装软件包：

```bash
npm install -g @antv/mcp-server-chart
```

启动服务器：

```bash
# For Streamable transport with custom endpoint
mcp-server-chart --transport streamable --port 1123
```

在 [app.py](../../app.py) 中配置 MCP Server：

```
"图表可视化": {
    "url": "http://localhost:1123/mcp",
    "transport": "streamable_http",
},
```
