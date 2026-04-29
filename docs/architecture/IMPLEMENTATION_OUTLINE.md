# Implementation Outline

This document is an informative companion to the foundational RFC.

The RFC is normative. This outline is intended to keep the first implementation
passes small and aligned.

## Initial Implementation Bias

- use standard library `dataclasses`
- avoid framework-driven architecture
- keep adapters thin at their public boundary
- allow private source-local assembly where necessary
- emit canonical graph nodes, edges, and claims directly

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

## Minimal HCL Surface

The first HCL implementation should support:

- `source` blocks
- `authority` blocks
- `policy` blocks
- `projection` blocks

It should not initially try to recreate the full `1.x` expression system.

## Recommended Early Build Order

1. core enums / literal sets for scopes, categories, tiers, modes
2. dataclass models for node, edge, claim, graph artifact
3. graph invariant validation helpers
4. authority resolution engine
5. artifact/JSON projector
6. minimal HCL parsing for source authority and projection declarations

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

The first projector after artifact/JSON should be simple enough to validate the
core architecture without forcing the internal model to resemble the target.

## What To Avoid Early

- rebuilding scheduler/UI concerns before the core exists
- introducing a generic workflow framework as the architecture center
- reintroducing nested target-write semantics from `1.x`
- broad field-level authority rules before scope/category rules are proven
