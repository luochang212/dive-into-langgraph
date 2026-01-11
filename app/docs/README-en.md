# Hands-on: Build a Streaming Chat Agent with LangChain

[中文](../README.md) | English

![gradio-app](../images/gradio_app.png)

> A super practical Agent Web APP. Fully local deployment, full control over your architecture and compute, squeezing the most out of LLMs.

## 💻 Tech Stack

- **Frontend**: `Gradio`
- **Backend**:
    - `LangChain`
    - `LangGraph`
- **MCP**: `fastmcp`

## 🔧 Toolset

- **tools**:
    - **Web search**: [tool_search](../tools/tool_search.py)
    - **Math**: [tool_math](../tools/tool_math.py)
- **MCP**:
    - **Role play**: [role-play](../mcp/role_play.py)
    - **Code execution**: [code-execution](../mcp/code_execution.py)
    - **Chart visualization**: [mcp-server-chart](../mcp/mcp-server-chart/README.md)
    - **Amap (Gaode Maps)**: [amap-maps](https://lbs.amap.com/api/mcp-server/summary)
    - **Filesystem**: [filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- **Middleware**:
    - **Dynamic system prompts**: [dynamic_prompt](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.dynamic_prompt)
    - **Todo list**: [TodoListMiddleware](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.TodoListMiddleware)
    - **Conversation summarization**: [SummarizationMiddleware](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.SummarizationMiddleware)

> \[!NOTE\]
>
> - **Chart visualization** and **Filesystem** MCPs are disabled by default. They require installing npm packages via `npx` before startup. I’m not confident about network speed in China, and I don’t want the startup to take too long, so they’re turned off. To use them, uncomment the `stdio` blocks for these two MCPs in [app.py](../app.py). The first startup may take a while; this is expected.
> - **Amap (Gaode Maps)** MCP is also disabled by default because it requires an `API_KEY` from the [Amap Open Platform](https://lbs.amap.com/api/mcp-server/create-project-and-key). Put `API_KEY` into your `.env` file, then uncomment the related code in `app.py` to run it.
> - `stdio` is ultimately a workaround. If you need long-running background services, `http` (Streamable HTTP) is recommended. Although `http` requires an extra port to serve `app.py`, it has lower latency and higher efficiency.

<!-- ## 👷 Skills -->

## 🚀 Getting Started

**Prerequisite**: `Python ≥ 3.10`

### 1) Configure environment variables

Create a `.env` file:

```bash
cp .env.example .env
```

Then register for [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/?tab=model#/model-market), obtain an `API_KEY`, and set it in the `.env` file.

### 2) Start the Agent and MCP Server

Install dependencies with uv and start the app:

```bash
# 1. Install uv
pip install uv -U

# 2. Sync the virtual environment with uv
uv sync

# 3. Run the app with uv
uv run app.py
```

<details>
  <summary>If uv installation fails, try installing with pip</summary>
  
  ```bash
  # 1. Install dependencies
  pip install -r requirements.txt -U -i https://mirrors.cloud.tencent.com/pypi/simple/
  # Notes:
  #   -i uses a mirror (full option: --index-url)
  #   -U upgrades to the latest package versions (full option: --upgrade)

  # 2. Run the app
  python app.py
  ```
  
</details>

## 🐒 Test Questions

See [query.md](./query.md)

## 🔭 Architecture

```text
.
├── README.md               # Main entry README
├── app.py                  # Main app entry
├── requirements.txt        # Project dependencies
├── .env.example            # Environment variable example
├── docs                    # Documentation
│   └── query.md
├── images                  # Image assets
│   ├── ai.png
│   ├── gradio_app.png
│   ├── gradio_app_raw.png
│   └── user.png
├── tests                   # Tests
├── logs                    # Logs
├── mcp                     # MCP modules
│   ├── mcp-server-chart
│   │   └── README.md
│   ├── code_execution.py
│   └── role_play.py
├── prompts                 # System prompts
│   ├── __init__.py
│   ├── prompt.py
│   ├── prompt_base.py
│   └── prompt_enhance.py
├── space                   # Filesystem read/write space
│   └── food.md
├── tools                   # Tools
│   ├── tool_math.py
│   └── tool_search.py
└── utils                   # Utilities
    ├── device_info.py
    ├── fix_deepseek.py
    ├── fix_dashscope.py
    ├── remove_html.py
    ├── think_view.py
    ├── tool_view.py
    └── web_ui.py
```

## 📦 Container Deployment

Before starting the container, make sure `.env` is properly configured.

### 1) Start the app

```bash
docker compose up -d
```

After initialization, open in your browser: [http://localhost:7860/](http://localhost:7860/)

### 2) Debug commands

```bash
# View running containers
docker ps

# View logs of the gradio-agent-container container
docker logs gradio-agent-container -f

# Stop and remove all containers for the current project
docker compose down

# Stop and remove all containers and local images for the current project
docker compose down --rmi local

# Rebuild and start in the background
docker compose up -d --build
```

## 🌱 Dependency Management

```bash
# 1. Ensure uv is installed
pip install uv -U

# 2. Initialize the project (creates a pyproject.toml with basic metadata)
uv init --name gradio-agent-app --description "Build a streaming chat agent with LangChain" --python 3.13

# 3. Update the dependencies section in pyproject.toml
# This automatically creates a .venv and generates uv.lock
uv add -r requirements.txt
```

## 📝 Changelog

- [x] **Polished frontend UI**: improved input box; improved ChatBot slider/margins/tool-call display/bubbles; improved background color
- [x] **Enhanced MCP**: added role-play MCP, code-execution MCP, Amap MCP, chart-visualization MCP, filesystem MCP
- [x] **Enhanced middleware**: added todo-list middleware; added conversation summarization middleware
- [x] **Context engineering**: pass sensitive info like API_KEY losslessly via runtime
- [x] **Multi-agent**: provide a subagent with its own context and search capability
- [x] **Standalone prompt module**: multiple system prompts; can inject current time, username, OS, etc.
- [x] **Dynamic system prompts**: update system prompts per query; time awareness down to seconds
- [x] **Error handling**: add LLM timeout limits; enable retries on LLM failures; MCP failures won’t exit and are summarized
- [x] **Welcome message**: show all tools (including MCP) names and descriptions on app open; show only names when too many tools exist
- [x] **Chain-of-thought capture**: developed [DashScopeChatOpenAI](../utils/fix_dashscope.py) to retrieve chain-of-thought for DashScope API
- [x] **Tool-call display optimization**: developed `_agent_events_optimize` in [app.py](../app.py) to optimize tool/MCP call input/output display
- [x] **Remove HTML tags from chat history**: remove HTML tags introduced for UI optimization to reduce context load
- [x] **Support local models**: added instructions for using Ollama in [ollama.md](./ollama.md)
- [x] **Support container deployment**: one-click deployment via docker compose
