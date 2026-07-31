# AGENTS.md

## How We Work

**Prefer the latest stable.** When choosing tool or dependency versions, use the latest stable release — don't pin older versions without a reason.

**Manage Python with uv.** All environments are created and updated with `uv`, using the project-level `.venv` from `uv sync`. Don't build ad-hoc environments with system `pip` or `conda`.

**Touch only what you must.** Don't refactor adjacent code or reformat what you didn't change. `ruff format` may only rewrite Python code blocks in `.md`/`.ipynb`; other languages and prose are never touched, and tutorial content or translations must not be altered.

**Verify before claiming done.** Don't say you ran something if you didn't. If you can't verify, say so.

**Consistency is load-bearing.** When a toolchain decision changes, find every place that assumed the old one — stale config is a bug that hasn't manifested yet. Keep `uv.lock`, the ruff config, and the documented versions in sync.

## What This Project Is

A 14-chapter Jupyter ebook on LangGraph 1.0 (LangChain + LangGraph), covering ReAct agents, state graphs, middleware, memory, context, MCP, supervisors, parallelization, RAG, web search, and deep agents — plus a companion Gradio chat app and an Agent Skill of the tutorial.

## Project Layout

- **Tutorial notebooks** — repo root, 14 chapters (`1.quickstart.ipynb` … `14.langgraph_cli.ipynb`)
- **Gradio app** — `app/`, its own uv project (Dockerfile, docker-compose)
- **MCP servers** — `mcp_server/`
- **Agent Skill** — `skills/dive-into-langgraph/`
- **Ebook config** — `myst.yml`

## Environment & Toolchain

**uv is the only environment manager.** Environments live in the project-level `.venv`:
- repo root: `uv sync` — tutorial/notebook dependencies (dev tools `ruff`, `jupyter` included)
- `app/`: `cd app && uv sync` — the Gradio app

**Prefer latest stable on build.** `uv sync` installs from the lock; when refreshing, prefer latest stable (`uv lock --upgrade-package <name>`). The dev toolchain is latest-stable — e.g. `ruff>=0.16.1`, whose 0.16 line formats Markdown code blocks by default and widened the default lint rules, so the root `.ruff.toml` pins `select = ["E4", "E7", "E9", "F"]` explicitly.

**`uv.lock` is the source of truth.** It is checked in. Preserve its registry/index when refreshing — never rewrite the whole lock's package URLs.

## Code Quality

**Format:** `ruff format .` — config in the root `.ruff.toml` (`line-length = 100`).
**Lint:** `ruff check .` — rules `E4/E7/E9/F`.

## Docs

The ebook is built with MyST:

```
npx --yes mystmd build --html --ci
```
