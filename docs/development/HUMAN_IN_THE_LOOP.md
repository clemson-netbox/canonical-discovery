# Human-In-The-Loop Development

This repository should be treated as a human-in-the-loop project.

That means agents assist with implementation, validation, and documentation, but
they are not the final authority on architecture, merge decisions, or runtime
acceptance.

## Working Model

The intended loop is:

1. a human defines or confirms the issue and desired outcome
2. an agent implements focused changes and updates related tests/docs
3. the agent reports what changed, what was verified, and what still needs human
   judgment
4. a human reviews the code, runtime evidence, and CI results
5. merge happens only after the human review and repo gates are satisfied

## What Agents Should Optimize For

Agents working in this repo should optimize for:

- small, reviewable changes
- explicit assumptions
- API-visible runtime validation
- strong debug instrumentation
- preserving architectural boundaries from the RFCs

## What Should Still Require Human Judgment

The following should not be treated as purely agent-autonomous decisions:

- architectural direction changes
- milestone or scope changes
- merge readiness
- interpretation of ambiguous production/runtime evidence
- security-sensitive deployment choices

## Validation Standard

When runtime behavior changes, the preferred evidence path is:

- CI results
- unit/integration test results
- API-retrieved run, job, lease, and artifact state
- projector or collector result artifacts

Direct database inspection is not the primary acceptance path.

## Review Standard

Agent work should be easy for a human reviewer to inspect.

That implies:

- issue-first changes
- dedicated branch or worktree per issue
- small commits
- linked docs/RFC updates when contracts change
- clear summary of what was implemented and how it was verified
