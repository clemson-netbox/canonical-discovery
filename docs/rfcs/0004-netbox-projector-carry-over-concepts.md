# RFC 0004: NetBox Projector Carry-Over Concepts

## 1. Abstract

This RFC defines which NetBox-specific operational and implementation concepts
from `1.x` should be carried into the `2.0` NetBox projector.

The goal is to preserve proven NetBox integration techniques without allowing
the projector to shape the canonical core or reintroduce `1.x` source-to-target
architecture.

## 2. Motivation

The NetBox projector is expected to be one of the first real target-facing
integrations in `2.0`.

Some `1.x` NetBox patterns were valuable because they reduced API churn,
improved runtime efficiency, and hid repetitive client details. Those ideas are
worth preserving explicitly so they are not rediscovered ad hoc.

At the same time, projector-specific carry-overs should stay scoped to the
projector and must not leak back into canonical models or authority behavior.

## 3. Goals

- preserve proven NetBox execution-side patterns from `1.x`
- keep NetBox-specific logic isolated to projector planning and execution
- document preferred client and caching strategy early
- avoid reintroducing NetBox-shaped internals into core code

## 4. Non-Goals

This RFC does not:

- define the full NetBox projection mapping yet
- require the first NetBox projector implementation to be feature-complete
- make Redis mandatory for all deployments on day one
- move canonical resolution logic into the NetBox projector

## 5. Core Rule

The NetBox projector consumes resolved canonical truth downstream.

It may optimize how it reads, caches, batches, and writes NetBox state, but it
must not redefine:

- canonical graph structure
- authority semantics
- cross-source truth resolution

## 6. Concepts To Preserve

### 6.1 Wrapped NetBox Client

Preserve the use of a dedicated wrapper around `pynetbox` rather than spreading
raw client calls throughout projector code.

In `2.0`, this means:

- NetBox API access should go through a small projector-local client layer
- `pynetbox` remains the underlying API library unless a later RFC replaces it
- the wrapper should centralize authentication, pagination behavior, lookup
  helpers, retry policy, and error normalization

The purpose is consistency and easier testing, not creating another domain
model.

### 6.2 Redis-Backed Caching

Preserve Redis-backed caching for expensive or repeated NetBox lookups.

In `2.0`, Redis caching is the preferred scaling path for the NetBox projector,
especially for:

- object lookup acceleration
- repeated foreign-key resolution
- reference-data reuse during one or many projection runs
- reducing unnecessary read pressure on NetBox

Redis should be treated as projector-side operational acceleration, not as a
source of truth.

### 6.3 Lookup And Resolution Helpers

Preserve the concept of reusable lookup helpers for common NetBox object
resolution tasks.

Examples include resolving:

- sites
- locations
- device roles
- manufacturers
- device types
- platforms
- tags
- tenants

In `2.0`, these helpers should live behind the projector wrapper/client layer
and should operate on projection-plan needs rather than on canonical-domain
types directly.

### 6.4 Idempotent Ensure-Style Writes

Preserve the operational pattern of safe repeated writes built around fetching,
comparing, creating, and updating target objects predictably.

In `2.0`, this means the NetBox projector should support:

- create-if-missing behavior where appropriate
- update-only-when-changed behavior
- stable matching keys for projected objects
- explicit handling of lossy mapping cases

This belongs to projector execution behavior, not to canonical resolution.

### 6.5 Batching And Change Minimization

Preserve the idea that the projector should minimize API traffic and avoid noisy
writes.

In `2.0`, the projector should prefer:

- cached reads
- bulk or grouped reads when supported
- minimal-field updates when practical
- avoiding rewrites when the target state is already correct

### 6.6 Artifact And Diff Visibility

Preserve the ability to inspect projector intent before or alongside target
execution.

For the NetBox projector, this should include support for:

- projection plan artifacts
- dry-run or no-write execution modes
- projector result artifacts summarizing created, updated, skipped, and failed
  operations

### 6.7 Retry And Failure Classification

Preserve operational awareness around transient API failures.

In `2.0`, the NetBox projector should centralize:

- retryable error classification
- rate-limit handling
- timeout handling
- useful status reporting back to the API

### 6.8 Dependency Ordering

Preserve the idea that some NetBox objects must exist before others can be
projected successfully.

In `2.0`, dependency ordering should be represented in projection planning and
execution ordering rather than in HCL object nesting.

Typical examples may include parent-before-child flows such as:

- site before location
- manufacturer before device type
- device before interface
- VRF or prefix before IP association where required by the chosen mapping

## 7. Concepts Not To Preserve

### 7.1 NetBox-Shaped Canonical Internals

Do not preserve internal core models that resemble NetBox resource trees.

### 7.2 Source-To-NetBox Mapping As The Primary Architecture

Do not preserve the mental model that the projector is the center of the
system.

The canonical graph and resolved truth remain upstream authorities.

### 7.3 HCL-Driven NetBox Write Trees

Do not preserve `1.x` HCL patterns where NetBox write orchestration is encoded
as nested transformation blocks.

### 7.4 Projector-Owned Truth Decisions

Do not preserve logic where the NetBox integration decides which source wins.

### 7.5 Cache As Authority

Do not treat Redis or local caches as a durable authority for NetBox truth.

Cache entries are accelerators only and must tolerate eviction, expiry, and
rebuild.

## 8. Preferred 2.0 Structure

The NetBox projector should likely be split into a few focused layers:

1. planner-facing translation from projection plan items to NetBox execution
   units
2. projector-local `pynetbox` wrapper
3. cache-backed lookup helpers
4. executor logic for create/update/reconcile behavior
5. result reporting back to the API

This keeps NetBox operational code cohesive without allowing it to shape the
core engine.

## 9. Redis Guidance

Redis is the preferred cache backend for the NetBox projector once remote or
repeated execution makes caching worthwhile.

The design should assume:

- Redis may be absent in the smallest local setups
- caching should be optional but supported cleanly
- cache misses must not break correctness
- cache invalidation should favor safety over aggressiveness

If Redis is unavailable, the projector may fall back to uncached behavior or a
lighter in-process cache depending on the deployment profile.

## 10. Early Contract Implications

This carry-over set suggests a few early implementation needs:

- a projector-local NetBox client abstraction
- explicit projection plan artifacts or work units
- projector result artifacts
- optional cache interface with a Redis implementation
- stable identity or matching rules for projected NetBox objects

## 11. Decision Summary

- preserve a `pynetbox` wrapper approach for NetBox access
- preserve Redis-backed caching as the preferred lookup-acceleration strategy
- preserve reusable lookup helpers, idempotent ensure-style writes, batching,
  diff visibility, retry handling, and dependency ordering
- do not preserve NetBox-shaped core internals, HCL-driven write trees, or
  projector-owned truth resolution
