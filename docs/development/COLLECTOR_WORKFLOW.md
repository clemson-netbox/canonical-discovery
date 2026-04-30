# Collector Workflow

Use this playbook when implementing or modifying collector behavior.

## Core Rules

- collectors are remote deployable services, not direct database writers
- collectors emit canonical nodes, edges, and claims only
- collectors use API-mediated check-in, claim, heartbeat, submission, and result
  reporting
- collectors do not resolve authority and do not perform projection

## Implementation Checklist

1. confirm the collector change aligns with RFC `0002`, `0005`, and `0006`
2. keep source-local assembly private to the adapter
3. ensure public output is canonical graph data only
4. ensure runtime status and artifacts are retrievable through the API
5. add tests for both canonical emission and control-plane behavior where
   relevant

## Validation Expectations

Preferred validation evidence:

- API-visible collector check-in state
- API-visible claimed job / lease state
- canonical graph submission artifact retrieval
- result submission status

## Common Mistakes To Avoid

- leaking source-private schemas into public contracts
- bypassing API queue or lease behavior
- embedding source precedence logic in collector code
- validating only through database inspection
