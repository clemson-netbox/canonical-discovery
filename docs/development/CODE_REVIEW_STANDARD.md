# Code Review Standard

Use this playbook when preparing changes for review or reviewing agent-produced
work.

## Review Priorities

Review should focus first on:

- correctness
- architectural boundary violations
- missing tests
- runtime validation gaps
- regressions in API-visible behavior or artifact contracts

## Expected Change Shape

Good reviewable changes are usually:

- issue-scoped
- based on a dedicated branch from `dev`
- small to moderate in size
- accompanied by tests when behavior changes
- accompanied by RFC or doc updates when contracts change

## Merge Expectations

Before merge, expect:

- CI green
- code review complete
- unit tests added or updated as needed
- runtime evidence retrieved when behavior changes
- Ruff format and lint repairs already applied locally for Python changes

## Red Flags

- target-specific logic leaking into canonical core
- hidden precedence logic in adapter or collector code
- direct database access used for UI or normal runtime validation
- large unstructured commits with weak evidence
