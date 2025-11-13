# LangGraph 1.0 完全指南

[EN](/README.md) | 中文

[LangGraph](https://github.com/langchain-ai/langgraph) 是由 [LangChain](https://github.com/langchain-ai) 团队开发的 Agent 开源框架。

## 一、安装依赖

```bash
pip -r requirements.txt
```

<details>
  <summary>依赖包列表</summary>

  以下为 `requirements.txt` 中的依赖包清单：

  ```text
  pydantic
  python-dotenv
  langchain[openai]
  langchain-mcp-adapters
  langgraph
  langgraph-cli[inmem]
  langgraph-supervisor
  langgraph-checkpoint-sqlite
  ipynbname
  fastmcp
  supervisord
  ```
</details>

## 二、章节目录

主教程：

|序号|章节|
| -- | -- |
| 1 | [快速入门](../1.quickstart.ipynb) |
| 2 | [状态图](../2.stategraph.ipynb) |
| 3 | [中间件](../3.middleware.ipynb) |
| 4 | [人机交互](../4.human_in_the_loop.ipynb) |
| 5 | [记忆](../5.memory.ipynb) |
| 6 | [上下文工程](../6.context.ipynb) |
| 7 | [MCP Server](../7.mcp_server.ipynb) |
| 8 | [多智能体：Supervisor 模式](../8.supervisor.ipynb) |
| 9 | [并行](../9.parallel.ipynb) |
| 10 | [Deep Agents](../10.deep_agents.ipynb) |
| 11 | [LangGraph CLI](../11.langgraph_cli.ipynb) |

教程中未提及的一些关键代码实现：

|代码|说明|
| -- | -- |
| [/tests/test_rag.py](../tests/test_rag.py) | 使用 `RAG` 将本地文档片段注入智能体 |
| [/tests/test_langmem.py](../tests/test_langmem.py) | 使用 `LangMeM` 管理智能体长期记忆 |
| [/tests/test_store.py](../tests/test_store.py) | 使用 `RedisStore` 快速读写长期记忆 |
| [/tests/test_router.py](../tests/test_router.py) | 实现一个简单的智能体路由 |

## 三、调试界面

启动 LangGraph CLI 提供的本地开发界面：

```
langgraph dev
```

更多介绍请参阅 [第11章](../11.langgraph_cli.ipynb)

## 四、参考文档

- [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangMem](https://langchain-ai.github.io/langmem/)
- [langgraph-101](https://github.com/langchain-ai/langgraph-101)
