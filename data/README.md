# Data Package

This folder contains the active v1 RAG data package for McGill Care Compass.

## Medallion Layout

| Layer | Status | Purpose |
| --- | --- | --- |
| Bronze | Generated locally, ignored by git | Raw HTML captures under `data/bronze/raw/rag_pages/`. |
| Silver | Active tracked review layer | Page, link, chunk, report, manifest, and source-input artifacts used for prototype retrieval. |
| Gold | Empty by design | Future reviewed, release-ready subset after explicit approval. |

## Current Corpus

The current Silver run contains 490 processed pages, 22,548 recorded links, 4,239 chunks, and a rebuildable local Chroma index. All chunks are `silver_unreviewed`; they are suitable for prototype retrieval and evaluation, not final advice.

Important tracked artifacts:

| Path | Purpose |
| --- | --- |
| `data/source-inputs/rag_seed_urls.csv` | Official seed URLs and source metadata. |
| `data/source-inputs/questionnaire_metadata_map.yml` | Shared intake-to-RAG metadata contract. |
| `data/silver/datasets/rag_pages.csv` | Page-level metadata and hashes. |
| `data/silver/datasets/rag_links.csv` | Link graph, crawl decisions, and skip reasons. |
| `data/silver/datasets/rag_chunks.csv` | Retrieval chunks and metadata. |
| `data/silver/reports/rag_run_manifest.json` | Run, schema, and config hashes. |
| `data/silver/reports/rag_pipeline_report.md` | Current run summary and commands. |
| `data/silver/reports/rag_corpus_quality_report.md` | Quality warnings for cleanup and review. |
| `data/silver/reports/rag_retrieval_examples.md` | Scenario examples for retrieval handoff. |

## Commands

Build or refresh the corpus:

```powershell
uv run python scripts/data/build_rag_corpus.py
```

Validate committed artifacts:

```powershell
uv run python scripts/data/validate_rag_corpus.py
```

Query the local corpus:

```powershell
uv run python scripts/data/query_rag_corpus.py --query "How do I access health insurance?" --category-id insurance --need-type costs_coverage
```

Refresh only questionnaire metadata after wording or mapping changes:

```powershell
uv run python scripts/data/build_rag_corpus.py --metadata-only
```

## Policy

- Do not commit Bronze raw captures, cleaned page text, SQLite files, or Chroma vector-store files unless policy changes.
- Keep CSVs, source inputs, run manifest, and reports reviewable in git.
- Use `review_status` to distinguish Silver evidence from future Gold recommendations.
- Update source-input configuration and rerun validation when taxonomy, source authority, questionnaire fields, or metadata rules change.
