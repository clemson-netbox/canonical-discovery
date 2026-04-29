# RFC 0003: 1.x Carry-Over Concepts for 2.0

## 1. Abstract

This RFC defines which ideas from `1.x` should be preserved in `2.0` and how
they should be re-expressed.

The goal is not compatibility with `1.x` structure, schemas, or HCL semantics.
The goal is to retain the parts of `1.x` that proved operationally and
architecturally valuable while aligning them with the canonical graph model from
RFC `0001` and the service boundaries from RFC `0002`.

## 2. Motivation

`1.x` remains useful as a proof of concept and migration reference.

However, carry-over discussions can become ambiguous unless the repository is
clear about the difference between:

- preserving a concept
- preserving an implementation shape

This RFC makes that distinction explicit so future work does not reintroduce
`1.x` architecture under new names.

## 3. Goals

- preserve high-value concepts from `1.x`
- reject `1.x` implementation patterns that conflict with `2.0`
- give future contributors a clear filter for migration ideas
- identify a few concepts that should shape upcoming contracts early

## 4. Non-Goals

This RFC does not:

- promise `1.x` config compatibility
- preserve `1.x` runtime structure
- define every migration path from `1.x` artifacts
- adopt `1.x` target mapping or orchestration patterns

## 5. Carry Over The Concept, Not The Shape

When evaluating a `1.x` idea, the default rule is:

1. preserve the operator or architectural value that `1.x` proved
2. re-express it in canonical graph, API, and service-boundary terms
3. reject it if carrying it forward would reintroduce target-shaped or
   source-specific architecture

## 6. Concepts To Preserve

### 6.1 Reusable Collectors

Preserve the idea that source execution should happen in reusable collector
workers rather than one-off source-specific scripts.

In `2.0`, this means:

- collectors are separate deployable services
- collectors run adapters remotely
- collectors check in, advertise capabilities, claim work, and submit canonical
  graph payloads to the API

### 6.2 Declarative Configuration

Preserve declarative configuration as the main operator-facing control surface.

In `2.0`, HCL should remain responsible for:

- source wiring
- source options
- authority policy
- deployment policy
- filtering and classification
- projection configuration

Do not preserve `1.x` HCL as the primary transformation or execution language.

### 6.3 Source-Local Assembly

Preserve the pattern where adapters can combine fragmented source observations
into a coherent internal source view before public emission.

In `2.0`, this means:

- private adapter assembly is allowed
- the public output is still canonical nodes, edges, and claims
- source-local assembly state is not a public contract

### 6.4 Multi-Source Enrichment

Preserve the value of combining multiple systems into a richer shared truth.

In `2.0`, this means:

- multiple sources contribute claims against shared canonical objects
- enrichment happens on canonical graph structures
- truth resolution is explicit rather than implied

### 6.5 Provenance And Explainability

Preserve and strengthen the ability to explain where data came from and why a
resolved value won.

In `2.0`, this means preserving:

- losing claims
- source identity
- timestamps
- supporting evidence or adapter context
- resolution reasoning

### 6.6 Dependency Awareness

Preserve the idea that some execution work depends on other work being present
or complete first.

In `2.0`, dependency awareness should live in:

- API job planning
- worker scheduling
- projector execution ordering

It should not live in nested HCL target-write semantics.

### 6.7 Idempotent Target Execution

Preserve the operational need for retries, batching, reconciliation-minded
writes, and safe repeated execution.

In `2.0`, this belongs to projector execution rather than to core truth
resolution.

### 6.8 Dry-Run And Artifact Output

Preserve artifact-style output as a first-class capability for:

- debugging
- review
- tests
- explaining planned changes

Artifact or JSON projection is especially valuable early because it validates
core behavior without requiring a live target.

### 6.9 Capability-Based Execution Placement

Preserve the concept that work should run where capability and connectivity
allow.

In `2.0`, this means:

- collectors advertise tags, capacity, and load
- the API matches and leases work based on capabilities
- the same pattern may later apply to projectors

### 6.10 Operational Run Lifecycle

Preserve the need for long-running operational concepts such as:

- scheduled runs
- background execution
- retries
- cleanup
- status reporting
- run history

In `2.0`, these belong in the API and worker operational plane defined by RFC
`0002`.

## 7. Concepts Not To Preserve

### 7.1 Target-Shaped Internal Models

Do not preserve internal models shaped around NetBox or any other target.

### 7.2 Source-Specific Precedence In Code

Do not preserve hidden precedence or authority logic embedded in adapters or
engine code.

Authority belongs in declarative policy.

### 7.3 HCL As A Transformation Engine

Do not preserve HCL as the center of normalization, prerequisites, object
nesting, or write orchestration.

### 7.4 Nested Target-Write Semantics

Do not preserve the idea that the architecture is fundamentally:

`source object -> transformed target payload -> nested target writes`

### 7.5 Coupled Runtime Concerns

Do not preserve tight coupling between:

- adapter execution
- orchestration
- target execution
- storage access
- UI data access

### 7.6 Direct Source-To-Target Mental Model

Do not preserve a mental model where sources effectively map directly into one
target system.

The canonical graph and resolved truth remain the center of the system.

## 8. Early Concepts That Should Shape Upcoming Contracts

The following concepts should influence upcoming implementation work early
because they affect multiple boundaries.

### 8.1 Run Model

The repository will likely need explicit concepts such as:

- `run`
- `job`
- `task`
- `claim`
- `lease`
- `heartbeat`
- `result`

Exact naming may change, but these concerns should be modeled deliberately.

### 8.2 Provenance Model

The repository will need a deliberate way to store and explain:

- raw evidence
- losing claims
- resolution reasons
- adapter context

### 8.3 Work Claiming Model

The collector claim model from RFC `0002` should be treated as a foundational
runtime pattern rather than an implementation detail.

Projectors may later use a related claim or lease pattern.

### 8.4 Artifact Model

The system will likely benefit from explicit artifact types for:

- canonical graph snapshots
- projection plans
- projection results

### 8.5 Config Layering

The repository should keep clear separation between:

- global configuration
- deployment policy
- source-specific configuration
- projection-specific configuration

## 9. Decision Filter For Future Work

When someone proposes reusing a `1.x` feature, ask:

1. what problem did it solve in `1.x`?
2. is that problem still real in `2.0`?
3. can the value be expressed in canonical graph, API, and policy terms?
4. would adopting it reintroduce target-shaped internals, source-specific truth
   rules, or HCL-driven orchestration?

If the answer to `4` is yes, preserve the concept differently or reject it.

## 10. Decision Summary

- preserve reusable collectors, declarative policy, source-local assembly,
  multi-source enrichment, provenance, dependency awareness, idempotent target
  execution, artifact output, capability-based placement, and operational run
  lifecycle concepts
- do not preserve target-shaped models, source-specific precedence in code,
  HCL-as-transformation-engine behavior, nested target-write architecture, or
  direct source-to-target thinking
- future migration ideas should be evaluated by preserving the value while
  re-expressing it in `2.0` terms
