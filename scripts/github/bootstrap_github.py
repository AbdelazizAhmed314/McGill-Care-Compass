"""Bootstrap GitHub labels, milestones, and milestone issues.

Run from the repository root after the remote repository exists and `gh auth status`
shows a valid token with `repo` and `project` scopes.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

LABELS: dict[str, tuple[str, str]] = {
    "data": ("0E8A16", "Service records, schema, source metadata, data validation"),
    "matching": ("1D76DB", "Routing logic, scoring, tie handling, recommendation behavior"),
    "ux": ("BFD4F2", "Intake flow, interface, response layout, usability wording"),
    "guardrails": ("D93F0B", "High-risk handling, unsupported cases, safety limitations"),
    "evaluation": ("5319E7", "Scenario tests, relevance rubric, evaluation results"),
    "deployment": ("006B75", "App deployment, environment setup, health checks"),
    "documentation": (
        "0075CA",
        "README, setup instructions, schema docs, progress-report evidence",
    ),
    "progress-report": ("FBCA04", "Work needed for a course progress report"),
    "qa": ("C2E0C6", "Testing, release checks, final verification"),
    "blocked": ("B60205", "Needs decision, review, data, or teammate input"),
}

MILESTONES: dict[str, tuple[str, str]] = {
    "Directory Milestone / Progress Report 1": (
        "2026-06-21T23:59:59Z",
        "Curated service directory, schema, quality checks, first progress evidence.",
    ),
    "Working Prototype / Progress Report 2": (
        "2026-07-05T23:59:59Z",
        "Intake flow, rule-based matching, grounded results, integrated prototype.",
    ),
    "Evaluation Package / Progress Report 3": (
        "2026-07-19T23:59:59Z",
        "Guardrails, maintenance reports, scenario evaluation, internal deployment.",
    ),
    "Usability Assessment / Progress Report 4": (
        "2026-07-26T23:59:59Z",
        "Usability sessions, findings, priority fixes, documentation.",
    ),
    "Presentation-Ready Release": (
        "2026-07-27T23:59:59Z",
        "Feature freeze, deployed app, maintenance package.",
    ),
    "Final Submission and Presentation": (
        "2026-07-30T23:59:59Z",
        "Final QA, rehearsal, backup demo, final upload.",
    ),
}


@dataclass(frozen=True)
class IssueSpec:
    title: str
    milestone: str
    labels: list[str]
    body: str


def run(args: list[str], *, capture: bool = False, dry_run: bool = False) -> str:
    """Run a command or print it during dry runs."""

    if dry_run:
        print("DRY RUN:", " ".join(args))
        return ""
    completed = subprocess.run(
        args,
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout if capture else ""


def parse_issues(path: Path) -> list[IssueSpec]:
    """Parse the 13 issue sections from the finalized issue-breakdown document."""

    text = path.read_text(encoding="utf-8")
    sections = re.split(r"(?=^### Issue \d+: .*$)", text, flags=re.MULTILINE)
    issues: list[IssueSpec] = []
    current_milestone = ""
    milestone_by_position: list[tuple[int, str]] = []
    for match in re.finditer(r"^## Milestone: (.+)$", text, flags=re.MULTILINE):
        milestone_by_position.append((match.start(), match.group(1).strip()))

    for section in sections:
        title_match = re.match(r"^### (Issue \d+: .+)$", section, flags=re.MULTILINE)
        if not title_match:
            continue
        start = text.index(section)
        for position, milestone in milestone_by_position:
            if position < start:
                current_milestone = milestone
            else:
                break
        labels_match = re.search(r"\*\*Suggested labels:\*\* (.+)", section)
        labels = []
        if labels_match:
            labels = [label.strip(" `") for label in labels_match.group(1).split(",")]
        issues.append(
            IssueSpec(
                title=title_match.group(1).strip(),
                milestone=current_milestone,
                labels=labels,
                body=section.strip(),
            )
        )
    if len(issues) != 13:
        raise ValueError(f"Expected 13 issues, found {len(issues)}")
    return issues


def repo_slug(repo: str | None, dry_run: bool) -> str:
    """Resolve owner/repo slug from gh when not passed explicitly."""

    if repo:
        return repo
    raw = run(["gh", "repo", "view", "--json", "owner,name"], capture=True, dry_run=dry_run)
    if dry_run:
        return "OWNER/McGill-Care-Compass"
    parsed = json.loads(raw)
    return f"{parsed['owner']['login']}/{parsed['name']}"


def create_labels(repo: str, dry_run: bool) -> None:
    for name, (color, description) in LABELS.items():
        run(
            [
                "gh",
                "label",
                "create",
                name,
                "--repo",
                repo,
                "--color",
                color,
                "--description",
                description,
                "--force",
            ],
            dry_run=dry_run,
        )


def create_milestones(repo: str, dry_run: bool) -> None:
    owner, name = repo.split("/", 1)
    existing_raw = run(
        ["gh", "api", f"repos/{owner}/{name}/milestones", "--paginate"],
        capture=True,
        dry_run=dry_run,
    )
    existing = set()
    if existing_raw:
        existing = {item["title"] for item in json.loads(existing_raw)}
    for title, (due_on, description) in MILESTONES.items():
        if title in existing:
            continue
        run(
            [
                "gh",
                "api",
                f"repos/{owner}/{name}/milestones",
                "-f",
                f"title={title}",
                "-f",
                f"due_on={due_on}",
                "-f",
                f"description={description}",
            ],
            dry_run=dry_run,
        )


def create_issues(repo: str, issues: list[IssueSpec], dry_run: bool) -> None:
    existing_raw = run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "title",
        ],
        capture=True,
        dry_run=dry_run,
    )
    existing = set()
    if existing_raw:
        existing = {item["title"] for item in json.loads(existing_raw)}
    for issue in issues:
        if issue.title in existing:
            print(f"Skipping existing issue: {issue.title}")
            continue
        args = [
            "gh",
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            issue.title,
            "--body",
            issue.body,
            "--milestone",
            issue.milestone,
        ]
        for label in issue.labels:
            args.extend(["--label", label])
        run(args, dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="GitHub repo slug, for example OWNER/McGill-Care-Compass")
    parser.add_argument(
        "--issues-file",
        default="docs/project/GitHub-Issue-Based-Task-Breakdown.md",
        help="Finalized issue-breakdown markdown file.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = repo_slug(args.repo, args.dry_run)
    issues = parse_issues(Path(args.issues_file))
    create_labels(repo, args.dry_run)
    create_milestones(repo, args.dry_run)
    create_issues(repo, issues, args.dry_run)


if __name__ == "__main__":
    main()
