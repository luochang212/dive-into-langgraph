同步项目环境：

```bash
uv sync
```

编写配置，启动 `supervisord` 维持后台任务。注意：配置里的 `directory=..` 相对 `supervisord` 的启动目录解析，因此必须先进入 `mcp_server/` 再启动，否则 MCP 服务会因找不到模块而启动失败：

```bash
cd mcp_server
uv run supervisord -c ./mcp_supervisor.conf
```

检查端口是否正常提供服务：

```bash
lsof -i :8000
lsof -i :8001
```

终止后台任务：

```bash
pkill -f supervisord
```
