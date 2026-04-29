# RFC 0006: Collector API Contract

## 1. Abstract

This RFC defines the initial API contract between remote collectors and the core
API service.

It focuses on the collector lifecycle:

- check-in
- job claim
- heartbeat
- result submission
- canonical graph submission

The goal is to define the collector-facing contract without binding the
implementation to a specific web framework or queue backend.

## 2. Motivation

RFC `0002` establishes that collectors check in, advertise capabilities, and
claim work from the API. Implementation needs a more concrete contract so the
runtime model is testable and so collector code can be built independently from
the API internals.

## 3. Goals

- define the minimum collector lifecycle contract
- keep the API authoritative for queueing and claims
- preserve canonical graph submission as the collector output
- support stateless collector processes apart from active claims and check-ins

## 4. Non-Goals

This RFC does not define:

- final HTTP path names
- final auth mechanism
- every error payload shape
- final batch-size or pagination limits

## 5. Collector Identity

Each collector instance should present a stable runtime identity for the life of
its process session.

Collector identity should be distinct from source identity.

A collector identity should support at least:

- a collector instance id
- a collector implementation or image version
- capability tags
- capacity metadata

## 6. Check-In Contract

Collectors should periodically check in with the API.

The check-in payload should include at least:

- collector instance id
- collector version
- supported capability tags or source tags
- maximum concurrent job capacity
- current active load
- last-known active leases or job ids if applicable
- optional placement metadata such as region or security domain

The API response should include at least:

- server-accepted collector identity
- collector session validity or registration status
- recommended next check-in interval
- optional server-side throttling or pause instructions

The API should treat check-ins as ephemeral operational state.

## 7. Claim-Work Contract

Collectors should request work from the API rather than being directly pushed
work.

The claim request should include enough information for safe matching, such as:

- collector instance id
- current load
- remaining available capacity
- capability tags
- optional preferred batch size

The claim response should either:

1. return no work
2. return one or more claimed jobs with lease information

Each claimed job should include at least:

- job id
- run id
- lease id
- lease expiry time
- job kind
- source or execution parameters needed by the collector
- artifact submission expectations

The collector must treat the returned lease as authoritative and time-bounded.

## 8. Heartbeat Contract

Collectors holding active leases should periodically heartbeat to the API.

The heartbeat should include at least:

- collector instance id
- lease id or active job id
- current execution status
- optional progress summary
- optional warning or degraded-state flags

The API response should allow at least:

- lease extension confirmation
- cancellation instruction
- backoff or shutdown instruction

## 9. Canonical Submission Contract

The collector’s primary successful output is canonical graph data.

Submission payloads should contain canonical-domain data only, such as:

- nodes
- edges
- claims
- source provenance context
- source run metadata

They must not contain:

- target-shaped payloads
- source-private schemas used as public contracts
- resolved truth decisions

The submission should support artifact-style transport even if the transport is
an API request body.

## 10. Result Submission Contract

Collectors should report terminal execution outcome back to the API.

The result payload should support at least:

- final status
- summary message
- warning list
- metrics such as counts and durations
- references to submitted artifacts if stored separately
- retryability hints where applicable

The API remains authoritative for final job state transitions, but collectors
provide the execution outcome data.

## 11. Failure And Expiry Behavior

If a collector loses connectivity or stops heartbeating:

- the API may expire the lease
- the job may return to a claimable state or move to terminal failure depending
  on policy
- late submissions from the collector should be validated against lease state

Collectors should be tolerant of lease loss and duplicate-submit rejection.

## 12. Idempotency Guidance

Collector-facing API actions should be designed to tolerate retries where
possible.

Especially important:

- repeated check-ins should refresh state, not create duplicated identities
- repeated result submission should not create duplicate terminal records
- repeated canonical artifact submission should be deduplicated or versioned
  safely

## 13. Minimal Lifecycle Sequence

The intended lifecycle is:

1. collector starts
2. collector checks in
3. collector requests claimable work
4. API grants a lease or returns no work
5. collector heartbeats while executing
6. collector submits canonical graph payloads
7. collector submits final result
8. API closes or expires the lease and updates job state

## 14. Decision Summary

- collectors identify themselves as runtime workers, not as sources
- collectors check in periodically with tags, capacity, and load
- collectors pull claimable jobs from the API
- leases and heartbeats are explicit API concepts
- collector success output is canonical graph submission plus result reporting
- the API remains authoritative for queue and job state
