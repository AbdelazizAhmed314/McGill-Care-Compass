# GitHub Bootstrap

Use this after `gh auth login -h github.com --web -s repo,project`.

1. Create the public repo from the local scaffold.
2. Create and push `develop`.
3. Create labels and milestones.
4. Create the 13 milestone issues from `docs/project/GitHub-Issue-Based-Task-Breakdown.md`.
5. Create `McGill Care Compass Delivery Board`.
6. Add the 13 issues to the board.
7. Enable project auto-add for future issues using the steps in [github-project-board.md](github-project-board.md).

The implementation script in `scripts/github/bootstrap_github.py` handles labels, milestones, and issues. Project fields may still require a one-time GitHub UI setup if the available `gh project` command cannot set every Project v2 field reliably.
