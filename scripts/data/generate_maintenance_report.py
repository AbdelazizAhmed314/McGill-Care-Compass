"""Generate maintenance reports for committed Silver RAG artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcgill_care_compass.maintenance import (  # noqa: E402
    MaintenanceReportPaths,
    write_maintenance_report,
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Generate McGill Care Compass maintenance reports.")
    parser.add_argument("--pages-csv", type=Path, default=ROOT / "data/silver/datasets/rag_pages.csv")
    parser.add_argument("--links-csv", type=Path, default=ROOT / "data/silver/datasets/rag_links.csv")
    parser.add_argument("--chunks-csv", type=Path, default=ROOT / "data/silver/datasets/rag_chunks.csv")
    parser.add_argument(
        "--markdown-report",
        type=Path,
        default=ROOT / "data/silver/reports/maintenance_report.md",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        default=ROOT / "data/silver/reports/maintenance_report.json",
    )
    return parser.parse_args()


def main() -> None:
    """Generate report files and print their locations."""

    args = parse_args()
    paths = MaintenanceReportPaths(
        pages_csv=args.pages_csv,
        links_csv=args.links_csv,
        chunks_csv=args.chunks_csv,
        markdown_report=args.markdown_report,
        json_report=args.json_report,
    )
    report = write_maintenance_report(paths)
    print("Maintenance report generated.")
    print(f"Pages: {report['counts']['pages']}")
    print(f"Links: {report['counts']['links']}")
    print(f"Chunks: {report['counts']['chunks']}")
    print(f"Markdown: {paths.markdown_report}")
    print(f"JSON: {paths.json_report}")


if __name__ == "__main__":
    main()
