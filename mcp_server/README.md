同步项目环境：

```bash
uv sync
```

编写配置，启动 `supervisord` 维持后台任务：

```bash
uv run supervisord -c mcp_server/mcp_supervisor.conf
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
