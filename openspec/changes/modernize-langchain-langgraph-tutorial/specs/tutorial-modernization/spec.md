## Purpose

Make every maintained tutorial and companion example teach the clearest current LangChain and LangGraph patterns, with executable behavior consistent across notebooks, scripts, the Agent Skill, and the Gradio app.

## ADDED Requirements

### Requirement: Type-safe LangGraph outputs
Maintained LangGraph invocation and streaming examples SHALL use the latest stable typed output version where the API offers one, and consumers SHALL read the documented typed envelope rather than legacy shape-dependent tuples or dictionaries.

#### Scenario: Multiple stream modes are consumed
- **WHEN** an app or example streams more than one LangGraph mode
- **THEN** it SHALL dispatch on the event type and read payload data from the unified envelope

#### Scenario: Values mode is demonstrated
- **WHEN** a tutorial labels an example as `values` mode
- **THEN** the code SHALL actually request state snapshots and inspect messages from the state payload

### Requirement: Least-privilege dynamic tools
Tool permissions known before a model call SHALL be enforced by filtering the tools exposed to that model call, while execution-time authorization SHALL remain inside a tool only when it depends on information unavailable earlier.

#### Scenario: Non-admin user invokes an agent
- **WHEN** runtime context identifies a user without permission for a privileged tool
- **THEN** the privileged tool SHALL be absent from the model request's tool schema

### Requirement: Current supervisor architecture
The multi-agent tutorial SHALL teach a supervisor as a main agent invoking context-isolated subagents as tools and SHALL explain when a router, handoff, skill, custom workflow, or single agent is preferable.

#### Scenario: Reader installs tutorial dependencies
- **WHEN** dependencies are synchronized
- **THEN** no dedicated supervisor wrapper package SHALL be required for the primary supervisor example

#### Scenario: Supervisor delegates a task
- **WHEN** the main agent calls a subagent
- **THEN** the example SHALL pass only task-relevant input and return a bounded result instead of sharing uncontrolled full history

### Requirement: Node reliability coverage
The StateGraph tutorial SHALL explain the execution order and intended use of retries, async node timeouts, post-retry error handlers, graph-wide node defaults, and cooperative graceful drain.

#### Scenario: Retryable node exhausts attempts
- **WHEN** a node continues to raise a configured retryable failure
- **THEN** the example SHALL show the error handler updating state or routing to a compensating node after retries are exhausted

### Requirement: Current middleware map
The tutorial SHALL present the current provider-agnostic middleware categories and SHALL recommend composing only the middleware required by an identified failure mode.

#### Scenario: Built-in middleware replaces custom infrastructure logic
- **WHEN** LangChain provides a production-ready middleware for retry, fallback, limits, context editing, tool selection, filesystem access, subagents, or testing
- **THEN** the tutorial SHALL prefer or reference the built-in implementation and reserve custom middleware for business-specific policies

### Requirement: Derived content stays synchronized
Notebook source SHALL remain the canonical tutorial content, and corresponding Agent Skill references and navigation summaries SHALL be regenerated or updated in the same change.

#### Scenario: Notebook prose or code changes
- **WHEN** a maintained notebook is modified
- **THEN** its generated reference Markdown and every chapter summary that describes the changed behavior SHALL match before verification passes

### Requirement: Verification proves repository consistency
The completed change SHALL pass notebook JSON and import smoke checks, Python formatting and lint, app tests, dependency consistency checks, stale-pattern searches, and the MyST HTML build.

#### Scenario: A stale old method remains
- **WHEN** verification finds `langgraph-supervisor`, maintained project `pip install` instructions, legacy multi-mode stream tuple parsing, or a reference that disagrees with its notebook
- **THEN** the change SHALL remain incomplete until the stale path is removed or explicitly justified in the spec
