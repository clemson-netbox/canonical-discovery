# RFC 0005: Run, Job, Task, Lease, and Result State Model

## 1. Abstract

This RFC defines the initial control-plane state model for operational work in
`2.0`.

It introduces the core runtime objects:

- `run`
- `job`
- `task`
- `lease`
- `heartbeat`
- `result`

These objects provide a shared vocabulary for the API, worker, collectors, and
projectors.

## 2. Motivation

RFC `0002` defines service roles and API-owned queueing, but implementation will
drift quickly unless the repository agrees on the basic runtime state model.

The system needs a small, explicit model for:

- scheduling work
- claiming work safely
- tracking liveness
- reporting success and failure
- preserving history without overloading canonical graph concepts

## 3. Goals

- define a small, consistent runtime vocabulary
- support API-owned queueing and leasing
- support collectors first and projectors later
- separate operational state from canonical graph state
- keep the model database-agnostic

## 4. Non-Goals

This RFC does not define:

- the final queue storage implementation
- every API endpoint in detail
- every failure code taxonomy
- cross-region or HA coordination behavior

## 5. Core Objects

### 5.1 Run

A `run` is the top-level record for one orchestrated execution request.

A run represents an operator-triggered, scheduled, or system-triggered attempt
to execute some discovery and optional projection work.

A run should include at least:

- stable run id
- trigger type
- creation time
- requested scope or selection
- desired work modes such as discovery-only or discovery-plus-projection
- status summary

### 5.2 Job

A `job` is a queueable unit of work owned by a run and assigned to one service
role.

A job is the primary object used for queueing and claiming.

A job should include at least:

- stable job id
- parent run id
- job kind
- target service role such as `collector` or `projector`
- capability tags required for execution
- priority
- status
- queue visibility timestamps

### 5.3 Task

A `task` is a logical child step inside a job.

Tasks exist so one queued job can track finer-grained execution work without
requiring every substep to be a separately leased queue item.

Examples:

- a source collection stage
- one source adapter invocation within a broader collector job
- one projection execution unit inside a projector job

Tasks should be visible in state and results, but jobs remain the lease target
unless a later RFC explicitly changes that.

### 5.4 Lease

A `lease` is the time-bounded claim that gives one worker instance the right to
execute one job.

A lease should include at least:

- lease id
- job id
- claimant identity
- claim start time
- expiry time
- most recent heartbeat time

Leases are operational control-plane objects, not canonical claims.

### 5.5 Heartbeat

A `heartbeat` is the liveness update associated with an active lease or service
check-in.

Heartbeats allow the API to distinguish active work from abandoned work.

### 5.6 Result

A `result` is the durable outcome record for a completed or terminal execution
attempt.

Results should preserve enough information to support:

- status reporting
- operator troubleshooting
- retries or follow-up work
- artifact references

## 6. Status Model

### 6.1 Run Statuses

Initial run statuses should be:

- `pending`
- `queued`
- `running`
- `succeeded`
- `failed`
- `partial`
- `cancelled`

Guidance:

- `pending`: run record exists but jobs are not fully created yet
- `queued`: one or more jobs are waiting for execution
- `running`: one or more jobs are leased or executing
- `succeeded`: all required jobs completed successfully
- `failed`: the run cannot complete successfully
- `partial`: some work succeeded but the requested outcome is incomplete
- `cancelled`: the run was intentionally stopped

### 6.2 Job Statuses

Initial job statuses should be:

- `pending`
- `queued`
- `claimed`
- `running`
- `succeeded`
- `failed`
- `expired`
- `cancelled`

Guidance:

- `pending`: job defined but not yet eligible to claim
- `queued`: job is claimable
- `claimed`: a lease has been granted but execution has not fully started
- `running`: active execution is in progress
- `succeeded`: job completed successfully
- `failed`: terminal failure
- `expired`: previous lease became stale and the job needs reassignment or final
  handling
- `cancelled`: intentionally stopped

### 6.3 Task Statuses

Tasks should use a similar but simpler set:

- `pending`
- `running`
- `succeeded`
- `failed`
- `skipped`
- `cancelled`

## 7. Lease Semantics

The API is authoritative for lease issuance and expiry.

Rules:

1. one active lease per claimable job
2. leases are time-bounded
3. lease holders must heartbeat before expiry
4. expired leases may be reassigned by the API
5. lease expiry does not by itself imply job failure

This supports safe recovery from collector or projector loss.

## 8. Run-To-Job Relationships

The initial model should assume:

- one run creates one or more jobs
- a collector job may produce downstream projector jobs
- job dependencies are explicit in API state, not implied by service behavior
- run status is a reduction over child job states

## 9. Retry Model

Retries should be represented explicitly in job state, not hidden inside worker
loops.

The model should support at least:

- attempt count
- max attempts
- last failure summary
- next eligible retry time

Whether retries create a new job row or a new attempt record is an
implementation detail, but the API must expose retry-aware state.

## 10. Result Model

Results should be structured enough to distinguish:

- completion status
- terminal reason
- warnings
- metrics such as counts or durations
- artifact references
- child task summaries

The result model must not overload canonical graph storage. Operational results
are separate from canonical domain data.

## 11. Minimal Field Guidance

The initial implementation should plan for these fields even if not every field
is stored on day one.

### 11.1 Run

- `run_id`
- `created_at`
- `trigger_type`
- `requested_mode`
- `status`

### 11.2 Job

- `job_id`
- `run_id`
- `job_kind`
- `service_role`
- `required_tags`
- `priority`
- `status`
- `attempt_count`

### 11.3 Lease

- `lease_id`
- `job_id`
- `claimant_id`
- `issued_at`
- `expires_at`
- `last_heartbeat_at`

### 11.4 Result

- `result_id`
- `job_id`
- `status`
- `summary`
- `metrics`
- `artifact_refs`

## 12. Decision Summary

- `run` is the top-level orchestrated execution record
- `job` is the primary queue and lease object
- `task` is a logical child execution record within a job
- `lease` is the API-issued time-bounded right to execute one job
- `heartbeat` updates liveness for an active lease or service session
- `result` is the durable execution outcome record
- operational state remains separate from canonical graph state
