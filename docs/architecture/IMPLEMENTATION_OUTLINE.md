# Implementation Outline

This document is an informative implementation companion to the RFC set.

The RFCs are normative. This outline is intended to keep the first
implementation passes small, ordered, and aligned with the current architecture.

## Initial Implementation Bias

- use standard library `dataclasses`
- avoid framework-driven architecture
- keep adapters thin at their public boundary
- allow private source-local assembly where necessary
- emit canonical graph nodes, edges, and claims directly
- keep control-plane state separate from canonical graph state
- treat artifact contracts as first-class boundaries, not ad hoc payloads

## Minimal Core Types

The earliest core implementation should likely define:

- `NodeScope`
- `EdgeType`
- `AuthorityTier`
- `AuthorityMode`
- `Category`
- `Node`
- `Edge`
- `Claim`
- `GraphArtifact`

These should be small, explicit, and strongly typed.

## Minimal Control-Plane Types

Once the canonical core exists, the first operational types should likely
define:

- `Run`
- `Job`
- `Task`
- `Lease`
- `Heartbeat`
- `Result`

These should remain operational control-plane models rather than leaking into
canonical graph contracts.

## Minimal Artifact Types

The first artifact contracts should likely define:

- `GraphArtifact`
- `ProjectionPlanArtifact`
- `ProjectionExecutionUnit`
- `ProjectionResultArtifact`

These should be durable, explicit structures rather than implicit API payload
shapes.

## Minimal HCL Surface

The first HCL implementation should support:

- `source` blocks
- `authority` blocks
- `policy` blocks
- `projection` blocks

It should not initially try to recreate the full `1.x` expression system.

The current parser direction assumes `python-hcl2` as the HCL text frontend and
then maps its loaded block output into typed config contracts.

## Service Boundary Reminder

Early code should preserve the logical split established by the RFCs even if the
first implementation runs in one Python process more often than the final
deployment model.

Keep boundaries clear between:

- canonical core logic
- API/application service logic
- collector runtime concerns
- projector execution concerns
- worker scheduling concerns

## Recommended Early Build Order

1. core enums / literal sets for scopes, categories, tiers, modes
2. dataclass models for node, edge, claim, graph artifact
3. graph invariant validation helpers
4. control-plane dataclasses for run, job, task, lease, heartbeat, and result
5. repository abstractions for canonical and control-plane persistence
6. minimal API application boundary around ingestion, queueing, and claiming
7. collector API contract implementation for check-in, claim, heartbeat, graph
   submission, and result submission
8. minimal worker loop that creates runs/jobs through the API
9. authority resolution engine
10. projection plan and result artifact models
11. artifact/JSON projection planning and execution
12. minimal HCL parsing for source authority and projection declarations

This order is intentionally biased toward proving canonical contracts first,
then introducing the smallest shared operational substrate before building
ingest, collector, and projection flows on top of it.

## Source Adapter Expectations

Adapters may internally:

- fetch raw source observations
- paginate/authenticate
- stitch fragmented records from the same source
- maintain internal private registries during assembly

Adapters must publicly emit:

- canonical graph nodes
- canonical graph edges
- claims

Adapters must not publicly emit:

- target-specific payloads
- source-private schemas consumed elsewhere
- hardcoded authority decisions

## Projection Expectations

Projectors should consume resolved canonical truth, not raw adapter output.

Projection planning should emit durable plan artifacts.

Projection execution should emit durable result artifacts.

The first projector after artifact/JSON should be simple enough to validate the
core architecture without forcing the internal model to resemble the target.

NetBox-specific execution patterns such as `pynetbox` wrapping, Redis-backed
caching, ensure-style writes, and dependency-aware execution ordering should be
implemented inside the projector boundary, not in the core.

## Collector Expectations

Collectors should be implemented against the API contract, not as direct
database writers or source-specific standalone scripts.

The first collector-facing implementation should prove:

- periodic check-in
- capability tag advertisement
- job claiming through the API
- lease heartbeat behavior
- canonical graph submission
- result submission

If the first implementation shortcuts deployment topology for local development,
it should still preserve these contract boundaries in code.

## Persistence Expectations

The first persistence implementation may use SQLite, but the code should be
written behind repository abstractions that do not assume SQLite-only behavior.

Do not let UI, collectors, or projectors depend directly on database schema
details.

## What To Avoid Early

- rebuilding scheduler/UI concerns before the core exists
- introducing a generic workflow framework as the architecture center
- reintroducing nested target-write semantics from `1.x`
- broad field-level authority rules before scope/category rules are proven
- leaking NetBox-specific or target-specific structures into canonical models
- skipping artifact contracts in favor of one-off request/response payloads
- collapsing control-plane job state into canonical graph storage
