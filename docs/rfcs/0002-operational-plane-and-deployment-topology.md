# RFC 0002: Operational Plane, Service Boundaries, and Deployment Topology

## 1. Abstract

This RFC defines the initial operational plane for `2.0`.

The system is split into container-deployable services with clear boundaries:

- collectors run source adapters remotely and submit canonical graph data back to
  the core over an API
- the API service runs the engine and owns persistence through an abstracted
  repository layer
- the web interface accesses all data through the API only
- a worker service runs scheduling and housekeeping tasks through the API
- projector execution is deployable separately from the API by default, while
  projection planning remains part of the core engine

This preserves the graph-first core from RFC `0001` while allowing distributed
deployment models where collectors and projectors may need to run near specific
sources or targets.

## 2. Motivation

The core RFC intentionally deferred UI, scheduler, job persistence, and runtime
topology.

That deferral is useful for early core work, but some structural decisions are
now needed because they change how code should be organized:

- source adapters should not be coupled to API process lifetime
- the engine should not be coupled to direct UI or database access patterns
- remote execution is required for some source and target placement models
- target connectivity constraints may differ from source connectivity
- operational tasks such as scheduling, retries, and cleanup need explicit
  ownership

## 3. Goals

- preserve RFC `0001` core semantics and layering
- support remote collector deployment in containers
- keep the engine behind a stable Python API boundary
- keep the web UI API-only with no direct database access
- allow SQLite initially while preserving a path to MySQL or PostgreSQL later
- support distributed projector deployment for security-sensitive targets
- keep projection planning separate from projection execution

## 4. Non-Goals

This RFC does not define:

- final authentication or authorization design
- Kubernetes-specific manifests or orchestration strategy
- final queue technology
- final API schema in detail
- HA or multi-region runtime guarantees

## 5. Service Topology

The initial service model is:

1. `api`
2. `web`
3. `worker`
4. `collector`
5. `projector`

These are logical service roles. A single deployment may run multiple instances
of `collector` or `projector`.

## 6. API Service

The `api` service is the system authority for persisted state and engine-driven
processing.

It should own:

- configuration loading
- canonical graph ingestion endpoints
- graph validation
- authority resolution
- persistence through repository abstractions
- projection planning
- job state transitions
- exposure of data for the UI and operators

It should not own:

- source-specific remote execution placement
- browser rendering
- scheduler loops
- target-specific connectivity assumptions for every projection target

The engine should be implemented as normal Python application code that the API
invokes, not as logic embedded in transport handlers.

## 7. Persistence Model

The engine must depend on an abstract repository or storage interface rather
than on SQLite-specific behavior.

Initial storage may be SQLite for simplicity.

The design must preserve a path to MySQL or PostgreSQL by avoiding:

- SQLite-only SQL features in the domain contract
- direct database access from the UI
- domain logic spread across ad hoc SQL in multiple services

Database access belongs to backend services only.

## 8. Web Service

The `web` service is a separate container.

It must access data exclusively through the API.

It must not:

- open direct database connections
- bypass API authorization or validation logic
- depend on internal storage schemas as its contract

This keeps UI evolution decoupled from persistence changes.

## 9. Worker Service

The `worker` service is a separate container for background operational tasks.

It should own:

- scheduler loops
- job creation triggers
- housekeeping such as cleanup of old jobs, artifacts, and transient state
- retry and timeout supervision where assigned by the runtime model

The worker should perform these actions through API or shared application
service interfaces, not by reaching directly into the database as an alternate
control path.

For `v0`, API-mediated behavior is preferred because it keeps business rules in
one place even if it is less optimized.

## 10. Collector Service

Collectors are remotely deployable containers that run source adapters.

Collectors participate in scheduling through a periodic check-in and claim
model coordinated by the API.

Collectors should:

- check in periodically to advertise liveness and execution capacity
- advertise capability metadata such as supported source tags, job capacity,
  current load, and runtime identity
- authenticate to source systems
- perform source-local assembly as defined by RFC `0001`
- emit canonical nodes, edges, and claims
- submit results and run status back to the API

Collectors should not:

- perform authority resolution
- write directly to the core database
- perform target projection
- expose source-private schemas as public contracts

The API contract between collectors and the core should exchange canonical graph
artifacts or equivalent canonical submission payloads, not target-shaped or
source-private objects.

### 10.1 Collector Capability Claims

Collector check-ins should publish operational claims that let the API make
placement decisions.

These claims should include at least:

- collector identity
- supported source tags or capability tags
- maximum concurrent job capacity
- current claimed or running load
- last check-in time
- optional placement metadata such as region, zone, or security domain

These are runtime scheduling claims, not canonical infrastructure claims from
RFC `0001`.

The API should treat them as ephemeral control-plane state used for matching and
load balancing.

### 10.2 Collector Job Claiming

Collectors should pull work from the API rather than receiving direct pushed
execution.

The API should provide the queueing mechanism for collector work, including:

- enqueuing jobs
- matching jobs against collector capability tags
- leasing or claiming jobs to eligible collectors
- preventing duplicate claims
- expiring or reassigning stale claims

The API should assign work in a load-aware manner using collector-advertised
capacity and current load.

The scheduler may decide that work should exist, but the API is the authority
for whether a job is queued, claimed, running, expired, or complete.

## 11. Projection Model

Projection remains downstream of resolved canonical truth as defined in RFC
`0001`.

This RFC further splits projection into two concerns:

1. projection planning
2. projection execution

### 11.1 Projection Planning

Projection planning belongs in the core engine and therefore in the `api`
service.

Planning consumes resolved truth and produces target-specific intended actions.

This preserves:

- consistent policy interpretation
- consistent lossy mapping decisions
- a single place for projection semantics

### 11.2 Projection Execution

Projection execution should be deployable as its own service role, `projector`.

This is the default target-facing model for `2.0` because it supports:

- network placement near protected targets
- different trust zones for different targets
- independent scaling and rollout of target integrations
- reduced pressure to embed every target dependency in the API container

Projector services should:

- receive planned projection work from the API
- perform target API writes or artifact publication
- report status, errors, and reconciliation results back to the API

Projector services should not:

- resolve source truth conflicts
- redefine projection planning semantics
- become alternate authorities for canonical state

### 11.3 Default Early Implementation

For early development, artifact or JSON projection may run in-process with the
API or worker because it has no remote target trust boundary.

Target-specific projectors should still be designed behind the same planner /
executor split so they can move out-of-process without changing core semantics.

## 12. Recommended Runtime Flow

The intended high-level flow is:

1. `worker` creates or schedules a run
2. `api` records the job and enqueues collector work
3. eligible `collector` instances check in, advertise capacity and tags, and
   claim work from the API
4. one or more `collector` instances fetch sources and submit canonical graph
   payloads
5. `api` validates, persists, enriches, and resolves truth
6. `api` performs projection planning for configured targets
7. one or more `projector` instances execute target-specific writes or artifact
   output
8. `api` remains the source of truth for run state, results, and history

## 13. Packaging Guidance

The repository should organize code by service boundary and shared core rather
than by one large runtime script.

The intended package split is conceptually:

- `core`
  - canonical models, validation, authority, projection planning
- `api`
  - transport handlers, application services, repository wiring
- `collectors`
  - adapter runners and collector runtime code
- `projectors`
  - execution-side target integrations
- `worker`
  - scheduler and housekeeping runtime code
- `web`
  - UI application

Exact package names may change, but these boundaries should remain clear.

## 14. Consequences

Positive:

- preserves a clean core boundary
- supports distributed deployment and security zoning
- keeps the UI decoupled from persistence
- makes database backend changes less invasive

Tradeoffs:

- more service coordination than a single-process design
- API contracts for collectors and projectors must be maintained carefully
- early local development will need lightweight orchestration even before full
  production deployment exists

## 15. Open Questions

Items intentionally left open for later RFCs or implementation work:

- API auth model for remote services
- whether projector work claims are leased through the API alone or via a queue
- artifact retention and cleanup policy details

## 16. Decision Summary

- collectors are separate deployable containers and submit canonical graph data
  to the API
- collectors check in periodically and advertise capability tags, capacity, and
  current load to the API
- the API owns queueing and load-balanced job claiming for collectors
- the API runs the engine and owns persistence behind an abstract database layer
- SQLite is acceptable first, but backend abstraction is required from the
  start
- the web UI is API-only and never talks directly to the database
- the worker is a separate service for scheduler and housekeeping concerns
- projection planning lives in the API/core
- projection execution should be deployable separately by default, with
  in-process artifact projection allowed early for simplicity
