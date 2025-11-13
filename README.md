# LangGraph 1.0 Tutorial

EN | [中文](/docs/README-zh.md)

[LangGraph](https://github.com/langchain-ai/langgraph) is an open-source agent framework developed by the [LangChain](https://github.com/langchain-ai) team.

## 1. Install Dependencies

```bash
pip -r requirements.txt
```

<details>
  <summary>Dependency List</summary>

  The following is the list of dependencies in `requirements.txt`:

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

## 2. Table of Contents

Main Tutorial:

|||
| -- | -- |
| 1 | [Quickstart](./1.quickstart.ipynb) |
| 2 | [State Graph](./2.stategraph.ipynb) |
| 3 | [Middleware](./3.middleware.ipynb) |
| 4 | [Human-in-the-Loop](./4.human_in_the_loop.ipynb) |
| 5 | [Memory](./5.memory.ipynb) |
| 6 | [Context Engineering](./6.context.ipynb) |
| 7 | [MCP Server](./7.mcp_server.ipynb) |
| 8 | [Multi-Agent: Supervisor Mode](./8.supervisor.ipynb) |
| 9 | [Parallel](./9.parallel.ipynb) |
| 10 | [Deep Agents](./10.deep_agents.ipynb) |
| 11 | [LangGraph CLI](./11.langgraph_cli.ipynb) |

Additional key implementations not covered in the tutorial:

| Code | Description |
| -- | -- |
| [/tests/test_rag.py](./tests/test_rag.py) | Use `RAG` to inject local document chunks into the agent |
| [/tests/test_langmem.py](./tests/test_langmem.py) | Manage long-term memory with `LangMem` |
| [/tests/test_store.py](./tests/test_store.py) | Read/write long-term memory quickly with `RedisStore` |
| [/tests/test_router.py](./tests/test_router.py) | Implement a simple agent router |

## 3. LangGraph CLI

Start the local development interface provided by LangGraph CLI:

```
langgraph dev
```

For more details, see [Chapter 11](./11.langgraph_cli.ipynb).

## 4. References

- [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangMem](https://langchain-ai.github.io/langmem/)
- [langgraph-101](https://github.com/langchain-ai/langgraph-101)
