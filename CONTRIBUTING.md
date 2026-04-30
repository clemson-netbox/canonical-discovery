# Contributing

## Philosophy

This repository is a `2.0` rewrite built from architecture-first decisions.

It should also be treated as a human-in-the-loop development environment where
agents assist implementation and validation, but humans remain the final
authority for review, merge, and acceptance.

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

## Issue-First Delivery Workflow

Development should be issue-first.

Expected workflow:

1. start from a GitHub issue
2. use a dedicated clean branch and isolated workspace or worktree for that issue
3. keep changes focused and incrementally reviewable
4. build unit tests alongside the code instead of deferring them
5. open a PR early and keep a steady review/update cycle

PRs should prefer small, coherent commits over large batch drops.

## Merge Gates

Merge should not occur until all of the following are true:

- CI checks are green
- required code review gates are satisfied
- relevant unit tests are present for the change
- runtime evidence has been retrieved through API-visible artifacts or status
  endpoints when the change affects runtime behavior

Direct database inspection is not the normal validation path.

## CI And Image Publishing

The repository should maintain GitHub Actions for both validation and image
publishing.

Current policy:

- commits should trigger CI validation
- commits should trigger runtime image builds
- PR builds should publish a PR-tagged image such as `:pr1234`
- branch builds should publish a branch-tagged image such as `:dev` or
  `:release-1.1`
- `main` should also publish `:latest`

These tags should represent the current state of the work under review so the
result can be exercised before merge.

## Testing Philosophy

The first code milestones should prioritize:

- canonical node/edge/claim contracts
- authority resolution behavior
- graph invariants
- projector contract behavior

Adapter tests should validate that adapters emit canonical graph data directly.
