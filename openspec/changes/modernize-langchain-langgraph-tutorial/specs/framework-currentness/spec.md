## Purpose

Ensure the repository continuously reflects the latest stable LangChain, LangGraph, and supporting toolchain releases without retaining obsolete compatibility paths.

## ADDED Requirements

### Requirement: Latest stable dependency baseline
The repository SHALL declare and lock the latest stable versions available for all direct dependencies at the time of each framework refresh, using uv as the only Python environment and dependency manager.

#### Scenario: Refresh finds newer stable packages
- **WHEN** `uv tree --outdated` reports a newer stable direct dependency
- **THEN** the dependency constraint and the applicable root or app lockfile SHALL be updated together

#### Scenario: Package index is preserved
- **WHEN** a lockfile is refreshed
- **THEN** existing registry and index URLs SHALL remain unchanged unless a separate change explicitly replaces them

### Requirement: Official sources define current behavior
Each framework refresh SHALL compare the repository against current official LangChain and LangGraph documentation, changelog entries, API references, and official repositories rather than relying on remembered APIs or third-party summaries.

#### Scenario: New release capability is discovered
- **WHEN** official sources document a capability absent from the tutorial
- **THEN** the change SHALL either add coverage or record a scoped follow-up with its stability status and intended tutorial location

#### Scenario: Existing method has a better official replacement
- **WHEN** official sources recommend a replacement for a method currently taught
- **THEN** the tutorial SHALL adopt the replacement and remove the superseded path

### Requirement: Stability status is explicit
The tutorial SHALL use stable APIs for default executable paths and SHALL label Alpha or Beta APIs wherever they are discussed.

#### Scenario: Officially recommended feature remains Beta
- **WHEN** an official guide recommends a Beta API for a specialized use case
- **THEN** the tutorial SHALL explain the benefit and stability trade-off without silently making it the production default

### Requirement: No compatibility-only paths
The repository SHALL NOT retain deprecated dependencies, examples, parsing branches, or setup instructions solely to support older LangChain or LangGraph releases.

#### Scenario: Breaking stable replacement is available
- **WHEN** adopting the current stable API breaks an older tutorial invocation or output shape
- **THEN** all maintained consumers SHALL migrate to the current shape and no old-shape fallback SHALL be added

### Requirement: uv-only setup contract
All maintained local setup and dependency-management instructions SHALL use `uv sync`, `uv add`, or other uv-native commands against project-level `.venv` environments.

#### Scenario: Reader follows any maintained setup entry point
- **WHEN** a reader uses the root README, app README, tutorial notebook, MCP README, Agent Skill, or build instructions
- **THEN** the instructions SHALL NOT direct them to create an environment or install project dependencies with system `pip` or Conda

### Requirement: Quality gates are enforced before merge
Repository-wide formatting and linting SHALL be defined once in version-controlled pre-commit configuration and SHALL run both from the local Git pre-commit hook and from CI.

#### Scenario: Contributor installs repository hooks
- **WHEN** the contributor runs the documented hook installation command
- **THEN** Git SHALL invoke the uv-locked format check and lint check before each commit

#### Scenario: A pull request bypasses local hooks
- **WHEN** CI evaluates the pull request
- **THEN** CI SHALL run the same version-controlled pre-commit checks across all maintained files and fail on formatting or lint errors
