# canonical-discovery

`canonical-discovery` is a clean-slate `2.0` rewrite of the earlier
multi-source infrastructure sync proof of concept.

The project is built around a simple idea:

- source adapters should be thin
- sources should emit a shared canonical graph directly
- multiple sources should enrich the same canonical objects
- authority should be explicit and declarative
- projection targets should consume resolved truth downstream

This repository intentionally does **not** treat the earlier `1.x` runtime as an
architectural base. `1.x` remains valuable as a proof of concept, test source,
and migration reference, but `2.0` is a rewrite rather than a refactor.

## Intended Direction

The core model for `2.0` is:

1. source adapters fetch and assemble source-native observations internally
2. adapters emit a shared canonical entity/relationship graph plus claims
3. multiple sources enrich the same canonical graph
4. authority is resolved from declarative HCL policy
5. projections publish resolved truth to target systems such as NetBox,
   Nautobot, ServiceNow, or artifact/JSON outputs

## Design Principles

- projection-neutral core
- graph-first canonical model
- layered enrichment
- source-configured authority
- mostly declarative HCL
- multi-target projection support
- thin adapters, no hidden target-specific precedence in source code

## Repository Status

This repository is in docs-first bootstrap mode.

The first commits establish:

- the foundational architecture RFC
- an implementation outline
- a roadmap for the initial milestones
- contributor expectations for RFC-first development

Code should follow those documents, not invent a parallel architecture.

## Initial Documentation

- `docs/rfcs/0001-canonical-graph-authority-and-hcl.md`
  - normative architecture RFC for `2.0`
- `docs/architecture/IMPLEMENTATION_OUTLINE.md`
  - initial implementation companion and milestone framing
- `docs/ROADMAP.md`
  - milestone roadmap
- `CONTRIBUTING.md`
  - contributor workflow and RFC expectations
