# Architecture Summary

This document is an informative architecture companion to the normative RFCs in
`docs/rfcs/`.

Use this file to understand the current intended system shape quickly.

Use the RFCs when implementation decisions need authoritative detail.

## Purpose

`canonical-discovery` `2.0` is a clean-slate rewrite built around a
projection-neutral canonical graph.

The system is designed to:

- run source adapters remotely in collectors
- ingest canonical graph data into an API-owned core
- resolve cross-source truth through declarative policy
- plan downstream projection work from resolved truth
- execute target-facing projection work separately when needed

## Source Of Truth

Normative architecture lives in:

- `docs/rfcs/0001-canonical-graph-authority-and-hcl.md`
- `docs/rfcs/0002-operational-plane-and-deployment-topology.md`
- `docs/rfcs/0003-1x-carry-over-concepts.md`
- `docs/rfcs/0004-netbox-projector-carry-over-concepts.md`
- `docs/rfcs/0005-run-job-task-and-lease-state-model.md`
- `docs/rfcs/0006-collector-api-contract.md`
- `docs/rfcs/0007-projection-plan-and-result-artifact-contract.md`

`IMPLEMENTATION_OUTLINE.md` is an implementation sequencing companion, not the
full architecture summary.

## System Shape

The system is split into clear service roles:

- `api`
- `worker`
- `collector`
- `projector`
- `web`

### API

The API is the control-plane authority.

It owns:

- persistence
- queueing and claims for collector work
- canonical graph ingestion
- graph validation
- authority resolution
- projection planning
- run and job state transitions
- runtime artifact retrieval for development and operator validation
- data access for the UI

### Worker

The worker owns background operational loops.

It is responsible for:

- scheduling runs
- creating or triggering work through the API
- housekeeping and cleanup

### Collectors

Collectors are remote deployable services that run source adapters.

Collectors:

- check in periodically
- advertise source tags, capacity, and current load
- claim work from the API
- run source-local assembly privately
- emit canonical nodes, edges, and claims
- submit canonical graph data and results back to the API

Collectors do not resolve truth and do not write directly to the database.

### Projectors

Projectors consume resolved truth downstream.

The architecture separates:

- projection planning in the API/core
- projection execution in projector services

Artifact/JSON projection may run in-process early, but the default model keeps
target-facing projection execution deployable separately.

### Web

The web interface is API-only.

It must not access the database directly.

## Core Data Flow

The intended end-to-end flow is:

1. `worker` schedules or triggers a `run`
2. `api` creates `job` records and enqueues collector work
3. eligible `collector` instances check in and claim jobs
4. collectors fetch source data and submit canonical graph payloads
5. `api` validates graph data and resolves truth
6. `api` creates projection plan artifacts
7. `projector` instances execute target-facing work from those plans
8. `api` records result artifacts and retains run history

## Canonical Core

The canonical graph is the center of the system.

Adapters emit:

- `nodes`
- `edges`
- `claims`

Authority resolution happens after canonical emission, not inside adapters.

The core must remain projection-neutral and must not drift into target-shaped
internal models.

## Policy Model

HCL remains the main declarative operator surface, but with a narrower role than
in `1.x`.

HCL should own:

- source wiring
- source options
- authority policy
- deployment policy
- filtering and classification
- projection configuration

HCL should not become the center of transformation, source merge, or target
write orchestration.

## Operational Model

The control plane uses explicit runtime objects separate from canonical graph
data:

- `run`
- `job`
- `task`
- `lease`
- `heartbeat`
- `result`

The API is authoritative for queue state, leasing, and expiry.

Collectors use a periodic check-in and claim model rather than direct pushed
execution.

## Artifact Model

Two artifact families are important:

- canonical graph artifacts from collectors
- projection plan and result artifacts for projector work

Projection planning should emit durable plan artifacts.

Projection execution should emit durable result artifacts.

Development and validation flows should retrieve runtime artifacts through the
API rather than relying on direct database inspection.

Debug instrumentation is expected at each stage so artifact inspection can
explain collector behavior, resolution outcomes, plan generation, and execution
results.

## Persistence Model

The API/core should depend on an abstract persistence layer.

SQLite is acceptable first.

The design should preserve a path to MySQL or PostgreSQL later.

The web interface must not couple itself to storage schemas.

## 1.x Carry-Over Rules

The default migration rule is:

- preserve valuable `1.x` concepts
- do not preserve `1.x` structure or target-shaped implementation patterns

Good carry-overs include:

- reusable collectors
- declarative policy
- source-local assembly
- multi-source enrichment
- provenance
- idempotent projection execution
- artifact output

Rejected carry-overs include:

- NetBox-shaped core models
- source-specific truth rules in code
- HCL as a transformation engine
- nested target-write architecture

## NetBox Projector Guidance

The NetBox projector is expected to preserve some execution-side patterns from
`1.x`, but only inside the projector boundary.

These include:

- a `pynetbox` wrapper
- Redis-backed lookup caching
- idempotent ensure-style writes
- dependency-aware execution ordering
- reusable lookup helpers

These decisions must not shape canonical core contracts.

## Implementation Bias

Early implementation should stay small and foundational.

The current documented bias is:

- standard library `dataclasses`
- strongly typed core enums and models
- graph invariant validation before broader runtime concerns
- authority resolution before complex control-plane features
- artifact/JSON projection before heavier target integrations

## What This Document Is For

Use this document when you need a quick view of:

- the major service boundaries
- the end-to-end system flow
- the separation between canonical truth and operational state
- the relationship between the API, collectors, and projectors

Use the RFCs when you need exact rules or when changing architecture.
