## Context

See `proposal.md` for motivation. The repository has two uv projects (root tutorials and `app/`), 14 source notebooks, generated Markdown references for chapters 1–11, a Gradio app, standalone examples, and MyST navigation. Some modernization edits already exist in the worktree; apply must reconcile and verify them rather than reimplement blindly.

LangChain 1.4 and LangGraph 1.2 are the current stable baselines. Some capabilities shipped inside stable packages remain explicitly Beta, notably LangChain MCP, Event Streaming v3, and `DeltaChannel`. The repository policy prefers the latest stable dependency releases but does not require experimental APIs to become default paths.

## Official Gap Inventory (2026-09-11)

### New capabilities absent or only mentioned

| Capability | Official status | Repository action |
| --- | --- | --- |
| Per-node run/idle timeouts, post-retry error handlers, graph-wide node defaults, and cooperative drain | Available in LangGraph 1.2 | Add a credential-free recovery example and explain the complete reliability chain in chapter 2 |
| Event Streaming v3 typed projections for messages, tool calls, values, subgraphs, and output | Beta; recommended by the current frontend guide for new apps | Record as the next frontend migration, retain stable v2 for the production Gradio path until the Beta warning is removed |
| `DeltaChannel` incremental checkpoint storage | Beta | Explain the checkpoint-size benefit and snapshot trade-off as follow-up scope; do not change the tutorial's persisted state format yet |
| Headless tools, generative UI, branching chat, join/rejoin streams, and message queues | Current LangChain frontend capabilities | Create focused future frontend/recovery scope rather than a catch-all chapter |
| Handoffs, Skills, Router, and custom multi-agent workflows | Current LangChain multi-agent patterns | Add selection guidance to chapter 8 and promote dedicated examples in later changes |
| Agent unit tests, integration tests, trajectory evaluation, and final-response evaluation | Current LangChain testing guidance | Add a future testing/evals chapter; retain and strengthen model-free app tests now |
| MCP elicitation, OAuth/per-user authentication, and MCP provenance/destructive metadata | LangChain 1.4 MCP namespace, Beta | Keep `MCPAdapter` migration; plan production security and elicitation coverage separately |
| ToolRuntime execution info and server info | Current LangChain tools API | Plan retry-aware and deployment-aware examples for chapter 6 |
| Expanded provider-agnostic harness middleware: tool/model retry and error handling, tool selection/search, shell/filesystem, subagents, file search, context editing, emulator, rubric grading | Mostly stable; rubric grading Beta | Refresh the middleware map and label Beta entries |

### Improvements over methods already taught

| Existing method | Current official direction | Repository action |
| --- | --- | --- |
| v1 invoke dictionaries and stream output whose shape changes with mode count | LangGraph 1.1 typed `GraphOutput` and uniform v2 `type/ns/data` stream parts | Migrate executable consumers to v2 |
| Dedicated `langgraph-supervisor` wrapper shown beside direct tool calling | Official wrapper README recommends direct supervisor tools for most new projects | Remove the package and wrapper example |
| Expose privileged tools, then reject calls inside the tool | Dynamically filter pre-registered tools from runtime context before model invocation | Replace the quickstart permission example |
| Hand-written infrastructure middleware used as the conceptual default | Compose current production-ready built-ins for known failure modes | Keep custom middleware for business-specific policy demonstrations |
| Standalone MCP adapter package | LangChain 1.4 `langchain.mcp.MCPAdapter` | Keep the completed built-in adapter migration and remove stale dependency names |
| `pip`/`requirements.txt` setup alongside uv | Project-level uv environments and lockfiles | Remove the parallel setup path |

Official sources: [Python changelog](https://docs.langchain.com/oss/python/releases/changelog), [LangGraph streaming](https://docs.langchain.com/oss/python/langgraph/streaming), [LangChain event streaming](https://docs.langchain.com/oss/python/langchain/event-streaming), [fault tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [tools](https://docs.langchain.com/oss/python/langchain/tools), [prebuilt middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in), [multi-agent](https://docs.langchain.com/oss/python/langchain/multi-agent), [MCP](https://docs.langchain.com/oss/python/langchain/mcp), and the [`langgraph-supervisor` repository](https://github.com/langchain-ai/langgraph-supervisor-py).

## Goals / Non-Goals

**Goals:**

- Establish one evidence-backed refresh pass that covers dependencies, teaching choices, executable consumers, derived references, and verification.
- Remove obsolete branches completely when the official replacement is materially better.
- Make stability boundaries visible so “latest” does not become “silently experimental.”
- Leave a task structure that can be repeated on later LangChain/LangGraph releases.

**Non-Goals:**

- Preserve output compatibility with older framework versions.
- Execute notebook cells that require paid model, search, or MCP credentials during CI.
- Add every official integration or provider-specific middleware.
- Replace Gradio or redesign the application UI in this change.

## Decisions

### Use official indexes and changelogs as the audit spine

Start with the official `llms.txt` indexes and Python release changelog, then open the relevant official guides and API references. This gives a finite capability inventory and avoids search-result bias. GitHub repositories are used when the package's maintenance recommendation is authoritative, as with `langgraph-supervisor`.

Alternative: compare only installed symbols. Rejected because symbol presence does not reveal recommendation status, stability, migration guidance, or conceptual gaps.

### Default to stable v2 streams; track v3 separately

Migrate the app and maintained stream examples to LangGraph `version="v2"`, whose `type/ns/data` envelope is stable. Document Event Streaming v3 as the target frontend architecture, but defer a production migration until the runtime no longer emits a Beta warning.

Alternative: immediately use v3 because the frontend guide recommends it. Rejected for the default app path because the API is still explicitly experimental and introduces projection-consumption concurrency that deserves its own tested change.

### Filter privileged tools before model invocation

Use runtime-aware model middleware to remove tools the current principal cannot call. Keep authorization checks at execution boundaries only where required for defense in depth or late-bound facts.

Alternative: expose every tool and raise `PermissionError` inside it. Rejected because it wastes tool-schema context, invites invalid model plans, and turns a known permission rule into a recoverable runtime failure.

### Remove the supervisor wrapper rather than documenting both paths

Keep the direct subagents-as-tools implementation as the canonical supervisor architecture and remove the dedicated dependency. Expand pattern-selection prose rather than preserving a second, less controllable example.

Alternative: retain the wrapper as a legacy appendix. Rejected because the project explicitly does not provide forward compatibility and the official repository positions the wrapper mainly as an upgrade aid.

### Keep notebooks canonical and regenerate references

Edit `.ipynb` sources, clear outputs for materially changed executable cells that were not rerun, then regenerate or faithfully update `skills/dive-into-langgraph/references`. Verification compares concepts and stale markers across both forms.

Alternative: edit notebook and reference files independently. Rejected because they will drift on the next refresh.

### Separate current implementation from future capability chapters

Land high-confidence replacements in existing chapters. Track larger uncovered domains—frontend recovery/generative UI, full multi-agent selection, testing/evals, and production MCP—as discrete follow-up tasks or future OpenSpec changes rather than inflating unrelated chapters.

Alternative: add a catch-all “latest features” chapter. Rejected because it would age quickly and mix unrelated learning progressions.

### Share one quality-gate definition between Git hooks and CI

Use uv-locked `pre-commit` with repository-local hooks that run `ruff format --check .` and `ruff check .`. CI invokes `pre-commit run --all-files`, so local and remote enforcement cannot silently select different commands or Ruff versions. Hooks check without rewriting files during a commit.

Alternative: duplicate Ruff commands in a handwritten Git hook and the workflow. Rejected because copied gate definitions drift and `.git/hooks` is not version-controlled.

## Follow-up OpenSpec Scope

Each item below should become its own OpenSpec change so its runtime contract, tests, and stability boundary stay explicit:

- **Frontend streams and recovery (stable + Beta):** adopt stable headless tools, branching chat, join/rejoin, and message queues; evaluate Event Streaming v3 projections only while clearly labeled **Beta**. Add generative UI in the same change only if its component protocol and reconnect behavior can be tested together.
- **Agent testing and evals (stable):** add unit tests with fake models, integration tests, trajectory evaluation, and final-response evaluation as a dedicated chapter and CI tier.
- **Production MCP (Beta):** cover elicitation, per-user OAuth/authentication, and provenance/destructive metadata. The LangChain MCP namespace is **Beta**, so examples must not silently become the default security boundary.
- **Incremental checkpoints (Beta):** benchmark `DeltaChannel` checkpoint-size reduction against its snapshot and migration trade-offs before replacing full-value channels.
- **Runtime-aware tools (stable):** extend chapter 6 with `ToolRuntime.execution_info` and `ToolRuntime.server_info` examples for retry-aware and deployment-aware tools.

## Risks / Trade-offs

- [Notebook outputs no longer match changed source] → Clear changed outputs unless the exact cell can run without external credentials; never present stale output as newly verified.
- [Experimental features are mistaken for omissions] → Record them with official stability labels and revisit on each stable release audit.
- [Mechanical uv cleanup alters third-party installation guidance] → Limit uv-only enforcement to maintained project setup; retain `pip` only inside historical quotations or external ecosystem explanations with explicit justification.
- [Removing the wrapper reduces breadth] → Replace breadth with official multi-agent pattern selection and a stronger direct example.
- [Two lockfiles drift] → Run outdated/sync checks independently in root and `app/`, preserving each configured index.
- [Partial pre-OpenSpec edits obscure task status] → During apply, inspect the worktree first and mark tasks complete only after their acceptance checks pass.

## Migration Plan

1. Inventory the existing worktree and map partial edits to tasks without discarding unrelated user changes.
2. Refresh root and app direct dependencies with uv while preserving indexes and synchronized lower bounds.
3. Complete tutorial and application API migrations, then remove all obsolete imports, dependencies, prose, and output assumptions.
4. Regenerate derived Agent Skill references and update navigation summaries.
5. Run targeted tests first, followed by root/app format and lint, notebook smoke checks, stale-pattern searches, dependency checks, and MyST build.
6. No rollback compatibility is promised. If a new stable API proves defective, fix forward on the current stable line; do not restore dual code paths.

## Verification Gates

Run these repository-wide stale-pattern searches during apply and again at closeout (excluding lockfiles, generated build output, and this OpenSpec change where the removed terms are intentionally documented):

```bash
rg -n 'langgraph-supervisor|langgraph_supervisor|create_supervisor|langchain-mcp-adapters|MultiServerMCPClient'
rg -n 'pip install|requirements\.txt|conda (create|install)'
rg -n 'for mode, payload in .*astream|async for token, .*\.astream'
rg -n 'stream_mode="(messages|values|updates)"' examples app skills/dive-into-langgraph/scripts
```

Positive gates are `uv tree --outdated --depth 1` in both uv projects, repository/index URL comparison, notebook smoke checks, focused model-free execution tests, app tests, Ruff format/lint, MyST build, `git diff --check`, and final targeted diff inspection.

## Verification Record

- All 14 notebooks passed nbformat validation; all 138 code cells were validated, and the 135 non-empty code cells passed an IPython-aware syntax compile smoke check.
- The chapter 2 recovery graph was executed without credentials: the configured node made exactly three attempts, the error handler routed to compensation, and v2 returned `GraphOutput(value={'status': 'recovered from ConnectionError'}, interrupts=())`.
- The quickstart permission middleware was exercised without a model API: a non-admin request exposed only `get_weather` and removed `math_add` before the handler.
- The full app unittest suite exercised the v2 multi-mode envelope without credentials. It emits the expected warning that `langchain.mcp` remains Beta.
- Model-backed notebook cells were intentionally not executed because chapters 1–14 include provider, search, Redis, MCP service, or external content dependencies. Changed model-backed cells were compile-checked; only the new credential-free reliability and middleware behaviors were executed directly.
