# RFC 0007: Projection Plan and Result Artifact Contract

## 1. Abstract

This RFC defines the initial artifact contract for projection planning and
projection execution results.

It introduces two primary artifact families:

- projection plan artifacts
- projection result artifacts

These artifacts create a stable seam between API-side planning and executor-side
projection work.

## 2. Motivation

RFC `0002` separates projection planning from projection execution. RFC `0004`
calls for explicit plan and result artifacts, especially for the NetBox
projector.

Without an explicit artifact contract, projectors will drift into ad hoc API
payloads or re-derive planning semantics locally.

## 3. Goals

- define a stable handoff from planner to projector
- preserve clear separation between planning and execution
- support dry-run, artifact export, and target execution
- support target-specific execution without leaking target shape into core truth

## 4. Non-Goals

This RFC does not define:

- final storage location for artifacts
- every target-specific plan field
- a complete diff grammar for every projector

## 5. Projection Plan Artifact

A projection plan artifact is the durable output of projection planning.

It represents intended target-facing work derived from resolved canonical truth.

The planner is responsible for producing it. Executors are responsible for
consuming it, not redefining it.

## 6. Projection Result Artifact

A projection result artifact is the durable execution outcome for one projection
attempt against one plan or plan slice.

It records what happened during execution without becoming a new source of
canonical truth.

## 7. Plan Artifact Requirements

A plan artifact should include at least:

- plan id
- parent run id
- target kind such as `artifact`, `netbox`, or another projector type
- planner version
- source resolved-truth snapshot reference or provenance reference
- one or more execution units
- dry-run compatibility indicator
- creation timestamp

The plan may be whole-run scoped or split into smaller units, but the artifact
must preserve stable identity and ordering intent.

## 8. Execution Units

A projection plan should be decomposable into execution units.

An execution unit is the smallest planner-owned unit the executor receives as a
coherent action bundle.

An execution unit should support at least:

- unit id
- target object family or operation group
- dependency references on prior units where needed
- intended operation set
- idempotent matching context
- payload or field-set data required for execution

The exact payload may be target-specific, but the envelope should remain
consistent across projectors.

## 9. Planner Responsibilities

The planner must:

- consume resolved canonical truth
- apply projection configuration and lossy mapping decisions
- determine ordering or dependency requirements
- emit execution-ready units
- avoid deferring core semantic decisions to the executor

The planner must not:

- require the executor to resolve source truth conflicts
- hide ordering assumptions that are required for correctness

## 10. Executor Responsibilities

The executor must:

- consume the plan artifact as authoritative intent
- perform target-facing reads and writes
- honor unit ordering and dependency constraints
- report results back in structured form

The executor may:

- optimize target reads through caching
- batch compatible operations
- skip no-op writes when target state already matches intent

The executor must not:

- redefine planner semantics
- silently invent missing plan dependencies
- become an alternate source of canonical truth

## 11. Result Artifact Requirements

A result artifact should include at least:

- result id
- related plan id
- related run id
- projector identity and version
- execution start and end timestamps
- terminal status
- unit-by-unit outcome summaries
- warnings and errors
- metrics such as created, updated, skipped, failed, and retried counts

## 12. Unit Outcome States

Each execution unit in the result artifact should support at least:

- `pending`
- `applied`
- `skipped`
- `failed`
- `blocked`

Guidance:

- `pending`: defined but not attempted in this execution
- `applied`: target work completed successfully
- `skipped`: no target change was required or policy chose not to apply
- `failed`: execution attempted and did not complete successfully
- `blocked`: not attempted because a dependency or prior condition failed

## 13. Dry-Run Behavior

The artifact model must support dry-run execution.

In dry-run mode:

- the planner output is still a real plan artifact
- the executor may validate lookups and dependency ordering
- the result artifact should describe intended operations and simulated outcomes
- no target mutation should occur

## 14. Artifact References

Plan and result artifacts should be referenceable from job and result state.

The operational model should support:

- artifact ids
- artifact type
- storage location or retrieval reference
- retention metadata where implemented

This allows run history and troubleshooting without embedding full artifacts in
every status row.

Artifact retrieval should be API-accessible so development and validation flows
can inspect plan and result artifacts without depending on direct database or
storage access.

## 15. Relationship To Canonical Artifacts

Projection artifacts are downstream from canonical graph artifacts.

They should reference canonical truth snapshots or equivalent resolved-truth
provenance, but they are not themselves canonical graph records.

## 16. Minimal Contract Shape

The initial logical shape should be thought of as:

1. planner emits `ProjectionPlanArtifact`
2. executor claims work for that artifact or a slice of it
3. executor emits `ProjectionResultArtifact`
4. API records result state and artifact references

Exact serialization format may change, but these object boundaries should stay
stable.

## 17. Decision Summary

- projection planning emits durable plan artifacts
- projection execution emits durable result artifacts
- execution units are planner-defined and executor-consumed
- dry-run is a first-class artifact mode
- projection artifacts should be retrievable through the API for validation and
  debugging
- projection artifacts remain downstream operational records, not canonical truth
