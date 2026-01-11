<div align="center">
    <img src="../img/social-preview.jpg" width="100%">
    <h1>Dive into LangGraph</h1>
</div>

<div align="center">
  <img src="https://img.shields.io/github/stars/luochang212/dive-into-langgraph?style=flat&logo=github" alt="GitHub stars"/>
  <img src="https://img.shields.io/github/forks/luochang212/dive-into-langgraph?style=flat&logo=github" alt="GitHub forks"/>
  <img src="https://img.shields.io/badge/language-English-brightgreen?style=flat" alt="Language"/>
  <a href="https://github.com/luochang212/dive-into-langgraph"><img src="https://img.shields.io/badge/GitHub-Project-blue?style=flat&logo=github" alt="GitHub Project"></a>
  <a href="https://github.com/luochang212/dive-into-langgraph/actions/workflows/deploy-book.yml"><img src="https://github.com/luochang212/dive-into-langgraph/actions/workflows/deploy-book.yml/badge.svg?branch=main" alt="deploy-book"/></a>
</div>

<div align="center">

[中文](../README.md) | English

</div>

<div align="center">
  <p><a href="https://www.luochang.ink/dive-into-langgraph/">📚 Online Reading</a></p>
  <h3>📖 LangGraph 1.0 Complete Guide</h3>
  <p><em>Build powerful agents from scratch</em></p>
</div>

---

## 1. Introduction

> In mid-October 2025, LangGraph released version 1.0. The team announced this as a stable release and expects the interfaces not to change significantly, so now is a great time to learn it.

This is an open-source ebook project designed to help Agent developers quickly master the LangGraph framework. [LangGraph](https://github.com/langchain-ai/langgraph) is an open-source agent framework developed by the LangChain team. It's powerful — memory, MCP, guardrails, state management, and multi-agent capabilities are all built in. LangGraph is typically used together with [LangChain](https://github.com/langchain-ai/langchain): LangChain provides the building blocks and tools, while LangGraph focuses on workflow orchestration and state management. Therefore, both libraries need to be learned. To help you ramp up quickly, this tutorial extracts the most important features from both libraries and organizes them into 14 chapters.

## 2. Installation

```bash
pip install -r requirements.txt
```

<details>
  <summary>Dependency list</summary>

  The following packages are listed in `requirements.txt`:

  ```text
  pydantic
  python-dotenv
  langchain[openai]
  langchain-community
  langchain-mcp-adapters
  langchain-text-splitters
  langgraph
  langgraph-cli[inmem]
  langgraph-supervisor
  langgraph-checkpoint-sqlite
  langmem
  ipynbname
  fastmcp
  bs4
  ```
</details>

## 3. Contents

Quick overview of the tutorial:

| # | Chapter | Main Content |
| -- | -- | -- |
| 1 | [Quickstart](../1.quickstart.ipynb) | Create your first ReAct Agent |
| 2 | [State Graph](../2.stategraph.ipynb) | Create workflows using StateGraph |
| 3 | [Middleware](../3.middleware.ipynb) | Implement four features with custom middleware: budget control, message truncation, sensitive word filtering, PII detection |
| 4 | [Human-in-the-Loop](../4.human_in_the_loop.ipynb) | Implement human-in-the-loop using built-in HITL middleware |
| 5 | [Memory](../5.memory.ipynb) | Learn how to create short-term and long-term memory |
| 6 | [Context Engineering](../6.context.ipynb) | Manage context using State, Store, Runtime |
| 7 | [MCP Server](../7.mcp_server.ipynb) | How to create MCP Server and integrate with LangGraph |
| 8 | [Supervisor Pattern](../8.supervisor.ipynb) | Two methods to implement supervisor pattern: tool-calling, langgraph-supervisor |
| 9 | [Parallelization](../9.parallelization.ipynb) | How to implement concurrency: node concurrency, `@task` decorator, Map-reduce, Sub-graphs |
| 10 | [RAG](../10.rag.ipynb) | Implement RAG: Vector Retrieval, Keyword Retrieval, Hybrid Retrieval |
| 11 | [Web Search](../11.web_search.ipynb) | Implement web search functionality: DashScope, Tavily, DDGS |
| 12 | [Deep Agents](../12.deep_agents.ipynb) | Brief introduction to Deep Agents |
| 13 | [Gradio APP](../13.gradio_app.ipynb) | Build a streaming chat agent app with Gradio |
| 14 | [Appendix: Debug UI](../14.langgraph_cli.ipynb) | Introduction to the debug UI provided by langgraph-cli |

> [!NOTE]
>
> **Commitment**: This tutorial is written entirely against LangGraph v1.0, with no residual content from v0.6.

## 4. Debug UI

`langgraph-cli` provides a debugging UI that can be launched quickly.

```bash
langgraph dev
```

See [Chapter 14](../14.langgraph_cli.ipynb) for details.


## 5. Hands-on Project

[Chapter 13](../13.gradio_app.ipynb) open-sources a streaming conversational agent app built with Gradio + LangChain. It looks like this 👇.

You can add more features to this app and customize your own agent. Code: [/app](../app/)

![](../app/images/gradio_app.png)

## 6. Further Reading

**Official Documentation:**

- [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangMem](https://langchain-ai.github.io/langmem/)

**Official Tutorials:**

- [langgraph-101](https://github.com/langchain-ai/langgraph-101)
- [langchain-academy](https://github.com/langchain-ai/langchain-academy)

## 7. How to Contribute

We welcome any form of contribution!

- 🐛 Report bugs — please open an Issue
- 💡 Suggest features — share your ideas
- 📝 Improve content — help enhance the tutorial
- 🔧 Optimize code — submit a Pull Request

## 8. License

This work is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
