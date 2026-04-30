# Projector Workflow

Use this playbook when implementing projection planning or execution behavior.

## Core Rules

- projection planning belongs in the API/core
- projection execution belongs in projector-side logic
- projectors consume resolved canonical truth downstream
- target-specific behavior must not redefine canonical truth or authority rules

## Implementation Checklist

1. confirm the change aligns with RFC `0002`, `0004`, and `0007`
2. decide whether the work belongs in planning or execution
3. preserve durable plan and result artifact boundaries
4. keep target-specific helpers inside the projector boundary
5. add tests for plan generation, ordering, and result reporting

## NetBox-Specific Reminders

- prefer the projector-local `pynetbox` wrapper
- use cache-backed lookup helpers where appropriate
- preserve idempotent ensure-style write behavior
- keep dependency-aware ordering explicit

## Validation Expectations

Preferred validation evidence:

- API-retrieved projection plan artifacts
- API-retrieved projection result artifacts
- clear result metrics such as created, updated, skipped, and failed

## Common Mistakes To Avoid

- moving truth resolution into projector code
- using ad hoc payloads instead of artifact contracts
- letting NetBox-shaped execution needs leak into canonical models
