# AGENTS.md

## Read This First

- Start with `README.md`, `CONTRIBUTING.md`, `docs/rfcs/0001-canonical-graph-authority-and-hcl.md`, `docs/rfcs/0002-operational-plane-and-deployment-topology.md`, `docs/rfcs/0003-1x-carry-over-concepts.md`, `docs/rfcs/0004-netbox-projector-carry-over-concepts.md`, `docs/rfcs/0005-run-job-task-and-lease-state-model.md`, `docs/rfcs/0006-collector-api-contract.md`, and `docs/rfcs/0007-projection-plan-and-result-artifact-contract.md`.
- Use `docs/architecture/ARCHITECTURE.md` for a fast system-level summary, but treat the RFCs as authoritative.
- Treat `docs/rfcs/` as normative architecture. `docs/architecture/` is informative. `docs/ROADMAP.md` is planning guidance only, not a compatibility promise.
- Use `docs/development/` playbooks for repeated implementation, validation, and review workflows.

## Current Repo State

- This repo is still in docs-first bootstrap mode, but the root toolchain is now defined in `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, and `.devcontainer/devcontainer.json`.
- Python is pinned to `^3.12`. Use Poetry inside the devcontainer for orchestration and Ruff for linting/formatting.
- `tool.poetry.package-mode = false` right now. Do not assume there is already an installable package or entrypoint.
- Do not run `poetry` on the host machine for normal repo work. Keep Poetry environments and installs inside the devcontainer flow.

## Delivery Workflow

- This repository is human-in-the-loop: agents assist, but humans remain the final authority for review, merge, and acceptance.
- Work issue-first.
- Use a dedicated clean branch and isolated workspace or worktree per issue.
- Keep commits small and reviewable.
- Build unit tests alongside code changes; do not treat tests as a later cleanup pass.
- Do not merge until CI, review gates, and runtime evidence checks are satisfied.
- When runtime behavior changes, validate using API-retrieved artifacts and status rather than direct database inspection.

## Verified Commands

- Build the devcontainer image with `docker compose build devcontainer`.
- Install dev dependencies in the container with `docker compose run --rm devcontainer poetry install --with dev`.
- Lint in the container with `docker compose run --rm devcontainer poetry run ruff check .`.
- Format in the container with `docker compose run --rm devcontainer poetry run ruff format .`.
- Build the runtime image with `docker compose build app`.
- The devcontainer uses the root `docker-compose.yml` service named `devcontainer`.
- The devcontainer runs `poetry install --with dev` on create.
- Poetry virtualenvs are stored in the container volume mounted at `/opt/poetry-venvs`, not in the repo checkout.
- The `devcontainer` service uses a bind mount for live repo edits. The `app` runtime image copies the repo into `/workspace` at build time and does not use the dev bind mount.
- GitHub Actions should validate lint/build on commits and publish runtime images tagged by PR number or branch name, with `latest` for `main`.
- There is still no verified root test or typecheck command until those tools are added to config.

## Architecture Guardrails

- `2.0` is a clean-slate rewrite. Do not preserve `1.x` engine structure, HCL semantics, or NetBox-shaped target-mapping patterns unless a newer RFC explicitly says to.
- Preserve `1.x` concepts, not `1.x` shapes: reusable collectors, declarative policy, source-local assembly, multi-source enrichment, provenance, and idempotent execution are good carry-over candidates; target-shaped models and HCL-driven orchestration are not.
- The canonical graph is the center of the system. Source adapters should emit canonical `nodes`, `edges`, and `claims` directly.
- Collectors are separate deployable services that run adapters remotely, check in periodically, advertise source tags/capacity/load, claim work from the API, and submit canonical graph data back to the API.
- The API owns engine processing, persistence, and the queue/claim mechanism for collector work. Web and worker flows should go through the API rather than bypassing it.
- Treat `run`, `job`, `task`, `lease`, `heartbeat`, and `result` as explicit control-plane concepts separate from canonical graph data.
- The web UI must stay API-only with no direct database access.
- Projection planning belongs in the API/core. Projection execution should be deployable separately by default, even if early artifact projection runs in-process.
- For the NetBox projector, preserve execution-side patterns like a `pynetbox` wrapper, Redis-backed lookup caching, idempotent ensure-style writes, and dependency-aware execution ordering, but keep them inside the projector boundary.
- Projection planning should emit durable plan artifacts, and projection execution should emit durable result artifacts rather than relying on ad hoc payloads.
- Runtime artifacts should be retrievable through the API during development and validation; do not assume direct database inspection is the normal debugging path.
- Preserve strong debug instrumentation at each stage so collector activity, authority resolution, projection planning, and projection execution can be explained from API-visible state.
- Source-local assembly is allowed inside adapters, but that private assembly state must not become a public schema consumed elsewhere.
- Do not hardcode source precedence or authority decisions in adapter code. Authority belongs in declarative HCL policy.
- Keep the core projection-neutral. Projectors consume resolved canonical truth downstream; adapters must not emit target-specific payloads.

## Implementation Bias For Early Code

- Prefer small foundational changes and minimal dependencies.
- The current docs explicitly bias early implementation toward standard library `dataclasses`, not framework-driven architecture.
- If you add code before more guidance exists, stay aligned with the documented build order: core enums/literals, dataclass models, graph invariant validation, minimal run/job/lease control-plane types, repository and API queue/claim substrate, authority resolution, projection artifacts and artifact/JSON projection, then minimal HCL parsing.
- Avoid building UI, scheduler, persistence, or broader control-plane/runtime concerns before the canonical core is stable.

## RFC-First Changes

- For architecture-bearing changes, read the active RFCs first.
- Update or add an RFC before implementing changes to architecture, contracts, or core terminology.

## Testing Focus When Code Arrives

- Prioritize tests for canonical node/edge/claim contracts, graph invariants, authority resolution behavior, and projector contracts.
- Adapter tests should prove adapters emit canonical graph data directly.
