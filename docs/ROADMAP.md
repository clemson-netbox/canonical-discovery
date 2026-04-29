# Roadmap

## Milestone 0: Foundational Docs

- repository intent and rewrite framing
- foundational RFC
- implementation outline
- contributor workflow

## Milestone 1: Canonical Core Contracts

- canonical node scope definitions
- canonical edge definitions
- canonical claim model
- graph invariants
- dataclass-based core models

## Milestone 2: HCL Configuration Surface

- source declaration shape
- authority declaration shape
- policy declaration shape
- projection declaration shape
- minimal parser contract

## Milestone 3: Ingest Pipeline

- adapter output contract
- canonical graph ingestion pipeline
- source-local assembly guidance
- graph artifact serialization

## Milestone 4: Authority Resolver

- scope/category authority ranking
- confidence-based ordering
- mode semantics: replace, fill_if_missing, merge, observe_only
- provenance preservation

## Milestone 5: Projection Framework

- projector interfaces
- projection planning contract
- artifact/JSON projector

## Milestone 6: First Target Projector

- initial NetBox projector
- explicit target-lossiness notes
- target mapping tests against canonical graph inputs

## Milestone 7: First Source Adapters

- one simple source
- one fragmented source
- one enrichment-focused source

## Milestone 8: Cross-Source Enrichment Validation

- `xclarity + vmware + nexus`
- `vmware + salt`
- `catc/nexus + supplemental source`

## Milestone 9: Operational Plane

- CLI shape
- batch/run orchestration
- persistence/runtime concerns
- control-plane design

This milestone is intentionally later. The canonical core comes first.
