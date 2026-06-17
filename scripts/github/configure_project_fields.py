"""Populate GitHub Project v2 fields for the 13 milestone issues."""

from __future__ import annotations

import argparse
import json
import re
import subprocess

MONTHS = {
    "June": "06",
    "July": "07",
}


def run(args: list[str], *, capture: bool = False) -> str:
    completed = subprocess.run(args, check=True, text=True, capture_output=capture)
    return completed.stdout if capture else ""


def field_lookup(project_number: int, owner: str) -> tuple[str, dict[str, dict]]:
    project_raw = run(
        ["gh", "project", "view", str(project_number), "--owner", owner, "--format", "json"],
        capture=True,
    )
    project_id = json.loads(project_raw)["id"]
    fields_raw = run(
        [
            "gh",
            "project",
            "field-list",
            str(project_number),
            "--owner",
            owner,
            "--format",
            "json",
        ],
        capture=True,
    )
    fields = {field["name"]: field for field in json.loads(fields_raw)["fields"]}
    return project_id, fields


def item_list(project_number: int, owner: str) -> list[dict]:
    raw = run(
        [
            "gh",
            "project",
            "item-list",
            str(project_number),
            "--owner",
            owner,
            "--format",
            "json",
            "--limit",
            "50",
        ],
        capture=True,
    )
    return json.loads(raw)["items"]


def parse_due_date(body: str) -> str:
    match = re.search(r"\*\*Due:\*\* (June|July) (\d+)", body)
    if not match:
        raise ValueError("Missing due date")
    return f"2026-{MONTHS[match.group(1)]}-{int(match.group(2)):02d}"


def parse_owner(body: str) -> str:
    match = re.search(r"\*\*Primary owners?:\*\* (.+)", body)
    if not match:
        return "Whole team"
    return match.group(1).strip()


def parse_task_ids(body: str) -> str:
    match = re.search(r"\*\*Maps to:\*\* (.+)", body)
    if not match:
        return ""
    return match.group(1).replace("`", "").strip()


def issue_number(title: str) -> int:
    match = re.match(r"Issue (\d+):", title)
    if not match:
        raise ValueError(f"Unexpected issue title: {title}")
    return int(match.group(1))


def set_text(project_id: str, item_id: str, field_id: str, value: str) -> None:
    run(
        [
            "gh",
            "project",
            "item-edit",
            "--project-id",
            project_id,
            "--id",
            item_id,
            "--field-id",
            field_id,
            "--text",
            value,
        ]
    )


def set_date(project_id: str, item_id: str, field_id: str, value: str) -> None:
    run(
        [
            "gh",
            "project",
            "item-edit",
            "--project-id",
            project_id,
            "--id",
            item_id,
            "--field-id",
            field_id,
            "--date",
            value,
        ]
    )


def set_single_select(
    project_id: str,
    item_id: str,
    field: dict,
    option_name: str,
) -> None:
    option = next(option for option in field["options"] if option["name"] == option_name)
    run(
        [
            "gh",
            "project",
            "item-edit",
            "--project-id",
            project_id,
            "--id",
            item_id,
            "--field-id",
            field["id"],
            "--single-select-option-id",
            option["id"],
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default="AbdelazizAhmed314")
    parser.add_argument("--project-number", type=int, default=2)
    args = parser.parse_args()

    project_id, fields = field_lookup(args.project_number, args.owner)
    for item in item_list(args.project_number, args.owner):
        content = item["content"]
        title = content["title"]
        body = content["body"]
        number = issue_number(title)
        workflow_status = "In Progress" if number in {1, 2, 3} else "Backlog"
        priority = "High" if number in {1, 4, 8, 13} else "Normal"

        set_single_select(project_id, item["id"], fields["Workflow Status"], workflow_status)
        set_single_select(project_id, item["id"], fields["Priority"], priority)
        set_date(project_id, item["id"], fields["Due Date"]["id"], parse_due_date(body))
        set_text(project_id, item["id"], fields["Owner"]["id"], parse_owner(body))
        set_text(project_id, item["id"], fields["Task IDs"]["id"], parse_task_ids(body))


if __name__ == "__main__":
    main()
