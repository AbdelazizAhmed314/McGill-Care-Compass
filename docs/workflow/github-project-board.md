# GitHub Project Board Setup

Project name: `McGill Care Compass Delivery Board`

## Fields

| Field | Values / Use |
| --- | --- |
| `Status` | `Backlog`, `Ready`, `In Progress`, `In Review`, `Blocked`, `Done` |
| `Milestone` | Mirrors GitHub milestone. |
| `Due Date` | Issue due date. |
| `Owner` | Primary owner or owner group. |
| `Reviewer` | Reviewer named in the issue body when available. |
| `Task IDs` | `MH`, `MY`, and `AA` task IDs mapped to the issue. |
| `Priority` | Default `Normal`; use `High` for milestone blockers. |
| `Evidence Link` | Link to PR, report, dataset, screenshot, or deployment evidence. |

## Auto-Add Workflow

After the project exists, enable the native GitHub Projects workflow:

1. Open the project.
2. Go to `Workflows`.
3. Enable `Auto-add to project`.
4. Set the filter to the `McGill-Care-Compass` repository.
5. Keep default status as `Backlog`.

The initial 13 issues should be added during bootstrap. This auto-add workflow is for future issues.
