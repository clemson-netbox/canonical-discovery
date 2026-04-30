# Branching Workflow

Use this playbook for normal repository development.

## Branch Roles

- `main` is the stable branch
- `dev` is the integration branch for active development
- normal issue work should branch from `dev`, not from `main`

## Branch Naming

Use a typed branch prefix so the purpose of the branch is obvious.

Preferred prefixes:

- `feature/`
- `bugfix/`
- `chore/`
- `docs/`
- `refactor/`
- `test/`

Include the issue number when practical.

Examples:

- `feature/issue-17-simple-source-adapter`
- `bugfix/issue-42-lease-expiry-state`
- `chore/issue-34-branching-workflow`

## Pull Request Targets

- normal implementation PRs should target `dev`
- `main` should receive reviewed and validated integration work rather than
  being the default base for issue branches

## Image Validation

The integrated branch image should come from the published registry build.

For shared validation of the current integrated environment, prefer the
published GHCR image for `dev`, such as:

- `ghcr.io/clemson-netbox/canonical-discovery:dev`

Branch and PR builds may also publish review-specific tags such as `:pr1234`.

Use local rebuilds when needed, but prefer the published branch image when the
goal is to validate what CI built for the current integrated branch state.
