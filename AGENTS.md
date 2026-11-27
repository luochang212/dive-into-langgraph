# AGENTS.md

## How We Work

**Prefer the latest stable.** When choosing tool or dependency versions, use the latest stable release — don't pin older versions without a reason.

**Manage Python with uv.** All environments are created and updated with `uv`, using the project-level `.venv` from `uv sync`. Don't build ad-hoc environments with system `pip` or `conda`.

**Touch only what you must.** Don't refactor adjacent code or reformat what you didn't change. `ruff format` may only rewrite Python code blocks in `.md`/`.ipynb`; other languages and prose are never touched, and tutorial content or translations must not be altered.

**Verify before claiming done.** Don't say you ran something if you didn't. If you can't verify, say so.

**Consistency is load-bearing.** When a toolchain decision changes, find every place that assumed the old one — stale config is a bug that hasn't manifested yet. Keep `uv.lock`, the ruff config, the documented versions, and the `skills-only` skill branch (see §Skill Distribution) in sync.

## What This Project Is

A 14-chapter Jupyter ebook on LangGraph 1.0 (LangChain + LangGraph), covering ReAct agents, state graphs, middleware, memory, context, MCP, supervisors, parallelization, RAG, web search, and deep agents — plus a companion Gradio chat app and an Agent Skill of the tutorial.

## Project Layout

- **Tutorial notebooks** — repo root, 14 chapters (`1.quickstart.ipynb` … `14.langgraph_cli.ipynb`)
- **Gradio app** — `app/`, its own uv project (Dockerfile, docker-compose)
- **MCP servers** — `mcp_server/`
- **Agent Skill** — `skills/dive-into-langgraph/`, mirrored to the `skills-only` orphan branch (see §Skill Distribution)
- **Ebook config** — `myst.yml`

## Environment & Toolchain

**uv is the only environment manager.** Environments live in the project-level `.venv`:
- repo root: `uv sync` — tutorial/notebook dependencies (dev tools `ruff`, `jupyter` included)
- `app/`: `cd app && uv sync` — the Gradio app

**Prefer latest stable on build.** `uv sync` installs from the lock; when refreshing, prefer latest stable (`uv lock --upgrade-package <name>`). The dev toolchain is latest-stable — e.g. `ruff>=0.16.7`, whose 0.16 line formats Markdown code blocks by default and widened the default lint rules, so the root `.ruff.toml` pins `select = ["E4", "E7", "E9", "F"]` explicitly.

**`uv.lock` is the source of truth.** It is checked in. Preserve its registry/index when refreshing — never rewrite the whole lock's package URLs.

## Code Quality

**Format:** `ruff format .` — config in the root `.ruff.toml` (`line-length = 100`).
**Lint:** `ruff check .` — rules `E4/E7/E9/F`.
**Git hook:** `uv run pre-commit install` once per clone. The versioned hook and CI both run `uv run pre-commit run --all-files`; hooks check but do not rewrite files.

## Skill Distribution

`origin/skills-only` is an orphan branch, not a copy of `main`. `npx skills add luochang212/dive-into-langgraph` clones it so users get the skill without the notebooks, app, or docs build. It holds only `skills/dive-into-langgraph/`, `README.md`, `.gitignore`, and `img/social-preview.webp`.

**A skill change is not done until that branch is refreshed.** After committing anything under `skills/dive-into-langgraph/` (or the mirrored `README.md`), run:

```
./scripts/sync_skills_branch.sh          # export from main, commit on the orphan branch, push
./scripts/sync_skills_branch.sh --check  # exit 1 when origin/skills-only is stale
```

The script exports the mirrored paths from `main` with `git archive`, commits them in a throwaway worktree, and pushes to `origin/skills-only`. Never hand-edit files on that branch — the next sync overwrites them, and `--check` (which needs network) is the only thing that would notice the drift.

## Docs

The ebook is built with MyST:

```
npx --yes mystmd build --html --ci
```
