<div align="center">
    <img src="./img/social-preview.jpg" width="100%">
    <h1>Dive into LangGraph</h1>
</div>

<div align="center">
  <img src="https://img.shields.io/github/stars/luochang212/dive-into-langgraph?style=flat&logo=github" alt="GitHub stars"/>
  <img src="https://img.shields.io/github/forks/luochang212/dive-into-langgraph?style=flat&logo=github" alt="GitHub forks"/>
  <img src="https://img.shields.io/badge/language-Chinese-brightgreen?style=flat" alt="Language"/>
  <a href="https://github.com/luochang212/dive-into-langgraph"><img src="https://img.shields.io/badge/GitHub-Project-blue?style=flat&logo=github" alt="GitHub Project"></a>
  <a href="https://github.com/luochang212/langgraph-tutorial/actions/workflows/deploy-book.yml"><img src="https://github.com/luochang212/langgraph-tutorial/actions/workflows/deploy-book.yml/badge.svg?branch=main" alt="deploy-book"/></a>
</div>

<div align="center">

中文 | [English](./docs/README-en.md)

</div>

<div align="center">
  <p><a href="https://luochang212.github.io/dive-into-langgraph/">📚 在线阅读地址</a></p>
  <h3>📖 LangGraph 1.0 完全指南</h3>
  <p><em>从零开始，动手实现强大的智能体</em></p>
</div>

---

## 一、项目介绍

> 2025 年 10 月中旬，LangGraph 发布 1.0 版本。开发团队承诺这是一个稳定版本，预计未来接口不会大改，因此现在正是学习它的好时机。

[LangGraph](https://github.com/langchain-ai/langgraph) 是由 LangChain 团队开发的开源智能体框架。它功能强大，你要的记忆、MCP、护栏、状态管理、多智能体它全都有。LangGraph 通常与 [LangChain](https://github.com/langchain-ai/langchain) 配合使用：LangChain 提供基础组件和工具，LangGraph 负责工作流和状态管理。因此，两个库的文档都需要学习。为了让大家快速入门，我将两个库的主要功能提取出来，分成 11 个章节进行介绍。

## 二、安装依赖

```bash
pip install -r requirements.txt
```

<details>
  <summary>依赖包列表</summary>

  以下为 `requirements.txt` 中的依赖包清单：

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

## 三、章节目录

本教程的内容速览：

| 序号 | 章节 | 主要内容 |
| -- | -- | -- |
| 1 | [快速入门](./1.quickstart.ipynb) | 创建你的第一个 ReAct Agent |
| 2 | [状态图](./2.stategraph.ipynb) | 使用 StateGraph 创建工作流 |
| 3 | [中间件](./3.middleware.ipynb) | 使用自定义中间件实现四个功能：预算控制、消息截断、敏感词过滤、PII 检测 |
| 4 | [人机交互](./4.human_in_the_loop.ipynb) | 使用内置的 HITL 中间件实现人机交互 |
| 5 | [记忆](./5.memory.ipynb) | 介绍如何创建短期记忆、长期记忆 |
| 6 | [上下文工程](./6.context.ipynb) | 使用 State、Store、Runtime 管理上下文 |
| 7 | [MCP Server](./7.mcp_server.ipynb) | 如何创建 MCP Server 并接入 LangGraph |
| 8 | [监督者模式](./8.supervisor.ipynb) | 两种方法实现监督者模式：tool-calling、langgraph-supervisor |
| 9 | [并行](./9.parallel.ipynb) | 如何实现多节点并行 |
| 10 | [Deep Agents](./10.deep_agents.ipynb) | 简单介绍 Deep Agents |
| 11 | [调试页面](./11.langgraph_cli.ipynb) | 介绍 langgraph-cli 提供的调试页面 |

未出现在上述章节但比较重要的代码，我放在仓库的 tests 目录下：

|代码|说明|
| -- | -- |
| [/tests/test_rag.py](./tests/test_rag.py) | 使用 `RAG` 将本地文档片段注入智能体 |
| [/tests/test_langmem.py](./tests/test_langmem.py) | 使用 `LangMem` 管理智能体长期记忆 |
| [/tests/test_store.py](./tests/test_store.py) | 使用 `RedisStore` 快速读写长期记忆 |
| [/tests/test_router.py](./tests/test_router.py) | 实现一个简单的智能体路由 |

> \[!NOTE\]
> 
> 承诺：本教程完全基于 LangGraph v1.0 编写，不含任何 v0.6 的历史残留。

## 四、调试页面

`langgraph-cli` 提供了一个可快速启动的调试页面。

```bash
langgraph dev
```

详见 [第11章](./11.langgraph_cli.ipynb)

## 五、参考文档

- [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangMem](https://langchain-ai.github.io/langmem/)
- [langgraph-101](https://github.com/langchain-ai/langgraph-101)
- [langchain-academy](https://github.com/langchain-ai/langchain-academy)
