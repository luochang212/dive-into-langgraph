# 实战：基于 LangChain 构建流式对话智能体应用

中文 | [English](./docs/README-en.md)

![gradio-app](./images/gradio_app.png)

> 超实用的 Agent Web APP。完全本地化部署，自主掌控架构和算力，榨干 LLM 潜力。

## 💻 技术栈

- **前端**：`Gradio`
- **后端**：
    - `LangChain`
    - `LangGraph`
- **MCP**：`fastmcp`

## 🔧 工具集

- **tools**：
    - **联网搜索**：[tool_search](./tools/tool_search.py)
    - **数学计算**：[tool_math](./tools/tool_math.py)
- **MCP**：
    - **角色扮演**：[role-play](./mcp/role_play.py)
    - **代码执行**：[code-execution](./mcp/code_execution.py)
    - **图表可视化**：[mcp-server-chart](./mcp/mcp-server-chart/README.md)
    - **高德地图**：[amap-maps](https://lbs.amap.com/api/mcp-server/summary)
    - **文件系统**：[filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- **Middleware**：
    - **动态系统提示词**：[dynamic_prompt](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.dynamic_prompt)
    - **任务列表**：[TodoListMiddleware](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.TodoListMiddleware)
    - **历史对话压缩**：[SummarizationMiddleware](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.SummarizationMiddleware)

> \[!NOTE\]
> 
> - **图表可视化** 和 **文件系统** 两个 MCP 默认关闭。因为这俩启动前，需要通过 `npx` 安装软件包。我对国内网速没有信心，担心启动时间太长，所以还是关了。如需使用，请在 [app.py](./app.py) 中解开它俩 `stdio` 部分的注释。解开注释后，首次启动时间较长是正常现象，请耐心等待。
> - **高德地图** MCP 也默认关闭。因为它需要 [高德开放平台](https://lbs.amap.com/api/mcp-server/create-project-and-key) 的 `API_KEY`。将 `API_KEY` 配置到 `.env` 文件后，解开 `app.py` 中的注释即可运行。
> - `stdio` 终究是权宜之计。如果需要长驻后台，建议使用 `http` (Streamable HTTP) 的传输方式。虽然使用 `http` 需要额外开端口为 `app.py` 提供服务，但是延迟更低、效率更高。

<!-- ## 👷 技能 (Skills) -->

## 🚀 启动方式

**前置条件：**`Python ≥ 3.10`

### 1）配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

然后注册 [阿里云百炼](https://bailian.console.aliyun.com/?tab=model#/model-market) 账号，获取 `API_KEY` 并配置到 `.env` 文件。

### 2）启动 Agent 和 MCP Server

使用 uv 安装依赖，并启动应用：

```bash
# 1. 安装 uv
pip install uv -U

# 2. 使用 uv 同步虚拟环境
uv sync

# 3. 使用 uv 运行应用
uv run app.py
```

<details>
  <summary>如果使用 uv 安装失败，可以使用 pip 安装</summary>
  
  ```bash
  # 1. 安装依赖包
  pip install -r requirements.txt -U -i https://mirrors.cloud.tencent.com/pypi/simple/
  # 注释：
  #   -i 为使用镜像源，全称 --index-url
  #   -U 为升级到最新包版本，全称 --upgrade

  # 2. 运行应用
  python app.py
  ```
  
</details>

## 🐒 测试问题列表

详见 [query.md](./docs/query.md)

## 🔭 架构

```text
.
├── README.md
├── app.py                  # 主应用入口
├── requirements.txt        # 项目依赖
├── .env.example            # 环境变量示例
├── docs                    # 文档目录
│   └── query.md
├── images                  # 图片资源
│   ├── ai.png
│   ├── gradio_app.png
│   ├── gradio_app_raw.png
│   └── user.png
├── tests                   # 测试目录
├── logs                    # 日志目录
├── mcp                     # MCP 模块
│   ├── mcp-server-chart
│   │   └── README.md
│   ├── code_execution.py
│   └── role_play.py
├── prompts                 # 系统提示词模块
│   ├── __init__.py
│   ├── prompt.py
│   ├── prompt_base.py
│   └── prompt_enhance.py
├── space                   # filesystem 读写空间
│   └── food.md
├── tools                   # 工具模块
│   ├── tool_math.py
│   └── tool_search.py
└── utils                   # 实用脚本模块
    ├── device_info.py
    ├── fix_deepseek.py
    ├── fix_dashscope.py
    ├── remove_html.py
    ├── think_view.py
    ├── tool_view.py
    └── web_ui.py
```

## 📦 容器部署

启动容器前，请确保已经配置好 `.env` 文件。

### 1）启动应用

```bash
docker compose up -d
```

初始化完成后，可在浏览器访问：[http://localhost:7860/](http://localhost:7860/)

### 2）调试命令

```bash
# 查看运行中的容器
docker ps

# 查看 gradio-agent-container 容器日志
docker logs gradio-agent-container -f

# 停止并删除当前项目的所有容器
docker compose down

# 停止并删除当前项目的所有容器、本地镜像
docker compose down --rmi local

# 重新构建镜像并在后台启动容器
docker compose up -d --build

# 进入容器的 bash 终端
docker compose exec -it gradio-agent bash
```

## 🌱 依赖管理

```bash
# 1. 确保已经安装 uv
pip install uv -U

# 2. 初始化项目，这会创建一个包含基础信息的 pyproject.toml 文件
uv init --name gradio-agent-app --description "基于 LangChain 构建流式对话智能体" --python 3.13

# 3. 更新 pyproject.toml 中的 dependencies 部分
# 这会自动创建 .venv 虚拟环境，并创建 uv.lock 文件
uv add -r requirements.txt
```

## 📝 更新记录

- [x] **优化前端展示效果**：优化输入框；优化 ChatBot 滑块、边距、工具调用显示、文字气泡框；优化背景颜色
- [x] **增强的 MCP**：加入角色扮演 MCP、代码执行 MCP、高德地图 MCP、图表可视化 MCP、文件系统 MCP
- [x] **增强的 Middleware**：加入任务列表中间件；加入历史对话压缩中间件
- [x] **上下文工程**：通过 runtime 无损传递 API_KEY 等敏感信息
- [x] **多智能体**：为 Agent 提供拥有独立上下文且具备搜索能力的 subagent（子智能体）
- [x] **独立提示词模块**：提供多种系统提示词，可注入当前时间、用户名、操作系统等信息
- [x] **动态系统提示词**：query 级别更新系统提示词，对时间的感知精确到秒
- [x] **错误处理**：增加 LLM 调用超时限制；开启 LLM 调用失败重试；MCP 运行失败免退出并总结失败原因
- [x] **欢迎语**：在用户打开 APP 时，展示所有工具（包括 MCP）的名称与描述。当工具过多时，仅展示工具名称
- [x] **思维链捕获**：针对 DashScope API 开发 [DashScopeChatOpenAI](./utils/fix_dashscope.py) 用于获取思维链内容
- [x] **工具调用展示优化**：开发 [_agent_events_optimize](./app.py) 函数，优化 Tool 和 MCP 调用时的输入、输出展示
- [x] **删除对话记录中的 HTML 标签**：删除为了优化前端展示效果引入的 HTML 标签，减轻上下文负担
- [x] **支持本地模型**：增加了使用 Ollama 部署本地模型的 [说明](./docs/ollama.md)
- [x] **支持容器部署**：支持使用 docker compose 一键部署智能体应用
