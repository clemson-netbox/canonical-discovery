# Contributing

## Philosophy

This repository is a `2.0` rewrite built from architecture-first decisions.

Contributors should assume:

- the canonical graph is the center of the system
- source adapters emit canonical graph data directly
- authority policy belongs in HCL, not in source adapter code
- projections are downstream consumers of resolved truth
- `1.x` compatibility is not the default goal

## RFC-First Workflow

For architecture-bearing changes:

1. read the active RFCs first
2. update or add an RFC when the change modifies architecture, contracts, or
   core terminology
3. implement only after the architectural shape is clear

Code should not introduce:

- source-private public schemas
- target-shaped canonical models
- hidden source precedence in adapter code
- ad hoc enrichment stages outside the documented pipeline

## Normative vs Informative Docs

- `docs/rfcs/` documents are normative
- `docs/architecture/` documents are informative implementation companions
- `docs/ROADMAP.md` is planning guidance, not a compatibility promise

## Early Development Guidelines

- prefer small foundational commits
- keep dependencies minimal unless they buy real leverage
- prefer standard library dataclasses for the first implementation pass
- do not build UI/control-plane concerns before the canonical core is stable
- do not reintroduce `1.x` target-mapping patterns under new names

## Commit Guidance

Early commits should stay focused:

- one architectural document or tightly related document set per commit
- one implementation concern per commit once code begins

## Testing Philosophy

The first code milestones should prioritize:

- canonical node/edge/claim contracts
- authority resolution behavior
- graph invariants
- projector contract behavior

Adapter tests should validate that adapters emit canonical graph data directly.
