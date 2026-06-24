# Git Workflow

## Branches

- `main`: release-ready code and documentation.
- `develop`: integration branch for active team work.
- Feature branches: created from `develop`.

## Branch Names

- `feature/issue-04-matching-prototype`
- `data/issue-01-rag-corpus`
- `docs/issue-11-readme`
- `fix/issue-07-empty-results`

## Pull Requests

Pull requests should:

- target `develop` unless preparing a release from `develop` to `main`;
- link the relevant GitHub Issue;
- explain evidence and tests;
- identify data, matching, and safety impacts;
- pass CI before merge.
