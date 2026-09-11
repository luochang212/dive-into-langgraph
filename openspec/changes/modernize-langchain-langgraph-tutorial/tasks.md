## 1. Reconcile Baseline and Official Evidence

- [x] 1.1 Inspect the dirty worktree, map every existing modernization edit to this change, and verify no unrelated user change is overwritten with `git diff --stat` and targeted diffs
- [x] 1.2 Recheck the official Python `llms.txt` indexes, release changelog, relevant API guides, and `langgraph-supervisor` recommendation; record new-vs-improved findings and official stability labels in the change artifacts
- [x] 1.3 Search all maintained files for deprecated imports, old stream shapes, stale dependency names, and contradictory setup paths; save the exact verification patterns for the final stale-pattern gate

## 2. Dependency and Toolchain Currentness

- [x] 2.1 Refresh root direct dependencies to latest stable releases with uv, update matching lower bounds and `uv.lock`, and verify `uv tree --outdated --depth 1` reports no stable direct-package updates
- [x] 2.2 Refresh `app/` direct and development dependencies with uv, update matching lower bounds and `app/uv.lock`, and verify the app's outdated report is clean
- [x] 2.3 Preserve the Tencent package index in both project configurations and lockfiles, verified by diffing all `source.registry` and configured index URLs
- [x] 2.4 Replace maintained project setup and dependency instructions with uv-native commands across root, app, notebooks, MCP READMEs, book instructions, and Agent Skill; verify no unjustified `pip install`, Conda, or nonexistent `requirements.txt` path remains

## 3. Stable API Migrations

- [x] 3.1 Migrate quickstart invoke/stream examples to LangGraph's stable typed v2 output, fix the mislabeled `values` example, clear unexecuted stale outputs, and verify all changed cells compile
- [x] 3.2 Migrate the Gradio app's multi-mode stream consumer to the v2 `type/ns/data` envelope and add a focused async test that fails on legacy tuple parsing
- [x] 3.3 Migrate maintained standalone and Agent Skill stream helpers to the v2 envelope and verify their sources compile and lint
- [x] 3.4 Replace tool-internal permission rejection in the quickstart with runtime-context dynamic tool filtering before model invocation, and verify a focused test or model-free middleware check hides the privileged tool for a non-admin
- [x] 3.5 Remove `langgraph-supervisor` from dependencies, imports, notebook cells, generated references, outputs, and summaries; verify a repository-wide search finds no maintained usage

## 4. Tutorial Coverage Improvements

- [x] 4.1 Expand the StateGraph chapter with LangGraph 1.2 retry/timeout/error-handler ordering, graph defaults, and graceful drain semantics; run the credential-free compensation example and verify its typed output
- [x] 4.2 Refresh the HITL chapter's provider-agnostic middleware map from the official current list, identify Beta entries, and verify every named class exists in the installed stable LangChain package or is labeled conceptual/Beta
- [x] 4.3 Expand the supervisor chapter's decision guidance to distinguish single agent, subagents, router, handoffs, skills, and custom workflows; verify links target the current official multi-agent pages
- [x] 4.4 Add concise follow-up scope in OpenSpec for frontend streaming/recovery and generative UI, agent testing/evals, production MCP elicitation/auth/metadata, `DeltaChannel`, and expanded ToolRuntime execution/server metadata, with each experimental API explicitly labeled

## 5. Canonical Content and Derived Artifacts

- [x] 5.1 Make notebook sources canonical and update the reference-generation workflow to run through uv without installing tools via system pip; verify it can regenerate selected references deterministically
- [x] 5.2 Regenerate or faithfully update Agent Skill references for every changed chapter, then compare headings, code markers, and removed APIs against their source notebooks
- [x] 5.3 Update root/app/English navigation summaries and the Agent Skill chapter map to reflect the single recommended supervisor path and current toolchain, verified by targeted stale-text searches

## 6. Verification and Closeout

- [x] 6.1 Run root `uv sync`, app `uv sync`, notebook smoke checks, app tests, `ruff format --check .`, and `ruff check .`; fix failures without reformatting prose or unrelated languages
- [x] 6.2 Run credential-free execution tests for v2 stream envelopes and the LangGraph 1.2 recovery graph, and record which model-backed notebook cells were intentionally not executed
- [x] 6.3 Run `npx --yes mystmd build --html --ci` and verify the 14-chapter navigation and changed pages build without broken references
- [x] 6.4 Run final repository-wide stale-pattern and dependency-currentness gates, inspect `git diff --check` and the complete diff, and mark this OpenSpec change ready for verification only when every requirement scenario is satisfied

## 7. Enforced Quality Gates

- [x] 7.1 Add the latest stable `pre-commit` to the root uv development dependencies and create one versioned configuration for repository-wide Ruff format and lint checks
- [x] 7.2 Make CI run the shared pre-commit configuration, remove the narrower duplicate app-only lint step, and document local hook installation and manual all-files execution
- [x] 7.3 Install the local Git hook, run it against all files, rerun CI-equivalent checks, and verify OpenSpec strict validation plus a clean quality-gate diff

## 8. Review Remediation

- [x] 8.1 Stop formatting generated reference code blocks independently from notebook cells, remove machine-local captured output from canonical notebooks, and regenerate references without changing executable indentation
- [x] 8.2 Complete the typed v2 migration for every maintained LangGraph graph and agent invocation/stream consumer, clear affected model-backed outputs, and update derived references
- [x] 8.3 Label the `langchain.mcp` namespace Beta wherever the built-in `MCPAdapter` path is taught, without relying on captured warning output
- [x] 8.4 Rerun deterministic reference checks, all repository gates, and both Standards and Spec review axes; commit only if no blocking finding remains
