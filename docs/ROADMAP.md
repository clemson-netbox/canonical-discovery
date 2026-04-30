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

## Milestone 3: Minimal Operational Substrate

- `run`, `job`, `task`, `lease`, `heartbeat`, and `result` state model
- repository abstractions for canonical and control-plane persistence
- collector check-in / claim / heartbeat API contract
- minimal API queueing and leasing behavior
- minimal worker loop for run and job creation

## Milestone 4: Ingest Pipeline

- adapter output contract
- canonical graph ingestion pipeline
- source-local assembly guidance
- graph artifact serialization

## Milestone 5: Authority Resolver

- scope/category authority ranking
- confidence-based ordering
- mode semantics: replace, fill_if_missing, merge, observe_only
- provenance preservation

## Milestone 6: Projection Framework

- projector interfaces
- projection planning contract
- artifact/JSON projector

## Milestone 7: First Target Projector

- initial NetBox projector
- explicit target-lossiness notes
- target mapping tests against canonical graph inputs

## Milestone 8: First Source Adapters

- one simple source
- one fragmented source
- one enrichment-focused source

## Milestone 9: Cross-Source Enrichment Validation

- `xclarity + vmware + nexus`
- `vmware + salt`
- `catc/nexus + supplemental source`

## Milestone 10: Web UI Foundations

- API-only web application shell
- run / job / lease status views
- basic artifact and result inspection
- initial canonical graph browsing views

## Milestone 11: Expanded Operational Plane

- CLI shape
- richer batch/run orchestration
- deeper persistence/runtime concerns
- advanced control-plane behavior and housekeeping

The canonical core still comes first, but the minimal operational substrate is
now intentionally earlier so ingest, collectors, and later projection work can
build on a shared API-owned run/job/lease framework. The UI should start after
that minimal substrate exists, but as its own API-only milestone rather than as
part of the substrate itself.
