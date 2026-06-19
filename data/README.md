# Data Package

This folder contains generated public evidence datasets and reports for McGill Care Compass.

## Start Here

- Curated recommendation directory: [datasets/curated_service_records.csv](datasets/curated_service_records.csv)
- Curated directory quality report: [reports/curated_service_directory_quality_report.md](reports/curated_service_directory_quality_report.md)
- Service-record schema: [../docs/workflow/service-record-schema.md](../docs/workflow/service-record-schema.md)
- Full investigation record: [reports/Consolidated-Data-Investigation-Report.md](reports/Consolidated-Data-Investigation-Report.md)
- Final project-facing evidence summary: [../docs/project/Data-Feasibility-and-Source-Evidence.md](../docs/project/Data-Feasibility-and-Source-Evidence.md)
- Source-input provenance notes: [source-inputs/README.md](source-inputs/README.md)

## Folder Map

| Folder | Contents |
| --- | --- |
| [datasets/](datasets/) | Generated CSV and JSON evidence datasets. |
| [reports/](reports/) | Data investigation, quality, and source-discovery reports. |
| [source-inputs/](source-inputs/) | Raw source-input policy and provenance notes. |

## Data Policy

- Commit generated public evidence and curated/sample service records needed for reproducibility.
- Do not commit bulky raw source inputs by default.
- Keep broad scraped records as discovery evidence, not direct recommendation records.
- Only curated service records should power app recommendations.

## June 21 Directory Commands

Build the curated milestone directory and quality report:

```bash
uv run python scripts/data/build_curated_service_records.py
```

Validate the curated directory:

```bash
uv run python scripts/data/validate_curated_service_records.py
```
