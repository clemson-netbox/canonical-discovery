# Runtime Validation

Use this playbook when validating behavior that touches collectors, API queueing,
authority resolution, or projection execution.

## Default Principle

Validation should be API-first.

Preferred evidence comes from:

- run, job, lease, and result state exposed through the API
- collector graph artifacts
- projection plan artifacts
- projection result artifacts
- structured debug instrumentation

## Normal Validation Flow

1. run the relevant unit and integration checks
2. inspect API-visible run and job state
3. retrieve related runtime artifacts through the API
4. review stage-level instrumentation for explanation, not just status
5. summarize what was proven and what remains uncertain

## Avoid

- relying on direct database inspection as the primary check
- treating a successful process exit as enough evidence
- skipping artifact retrieval when the change affects runtime behavior
