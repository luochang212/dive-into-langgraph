## Why

LangChain and LangGraph now evolve through frequent stable minor releases, while the tutorial still contains several pre-1.2 patterns, an officially de-emphasized supervisor wrapper, and installation instructions that contradict the repository's uv-only toolchain. The repository needs an explicit, repeatable contract for tracking official stable APIs so tutorial examples remain authoritative instead of merely runnable.

## What Changes

- **BREAKING** remove `langgraph-supervisor` and teach only the official subagents-as-tools supervisor pattern.
- **BREAKING** standardize project setup on `uv sync`, `pyproject.toml`, and checked-in `uv.lock`; remove `pip` and nonexistent `requirements.txt` paths from maintained instructions.
- Adopt LangGraph's stable `version="v2"` invoke/stream envelopes in executable examples and the Gradio app.
- Replace post-selection tool permission failures with pre-model dynamic tool filtering through middleware and runtime context.
- Add LangGraph 1.2 node reliability coverage: retry, timeout, error handling, graph defaults, and graceful drain semantics.
- Refresh the built-in middleware map and distinguish stable defaults from Beta capabilities such as Event Streaming v3, `DeltaChannel`, and rubric grading.
- Track uncovered official capabilities as explicit follow-up tasks: frontend streaming/recovery, multi-agent pattern selection, agent testing/evals, production MCP, and expanded ToolRuntime metadata.
- Upgrade all declared dependencies and development tools to their latest stable releases while preserving the configured package index.
- Enforce repository-wide formatting and linting through one versioned pre-commit configuration shared by local Git hooks and CI.

## Capabilities

### New Capabilities

- `framework-currentness`: Defines how dependency versions and tutorial API choices stay aligned with the latest stable LangChain and LangGraph releases.
- `tutorial-modernization`: Defines the observable teaching and example behavior for current streaming, permissions, reliability, middleware, multi-agent, MCP, and testing guidance.

### Modified Capabilities

None. This repository did not previously contain OpenSpec capability specs.

## Impact

- Tutorial notebooks `1` through `14`, especially quickstart, StateGraph, HITL, MCP, supervisor, streaming, Deep Agents, Gradio, and CLI chapters.
- Derived Agent Skill references under `skills/dive-into-langgraph/`.
- Root and app `pyproject.toml` / `uv.lock`, setup documentation, example scripts, Gradio streaming code, and tests.
- Existing users following `pip`, v1 stream tuple parsing, or `langgraph-supervisor` examples must migrate; no compatibility layer will be retained.
