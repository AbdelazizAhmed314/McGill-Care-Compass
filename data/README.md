# Data Package

This folder contains the active v1 RAG data package for McGill Care Compass.
The previous static record files have been removed. The current data layer is a
medallion pipeline that ingests official source pages,
creates source-grounded chunks, and builds a local vector index.

## Medallion Layout

| Layer | Path | Contents | Commit policy |
| --- | --- | --- | --- |
| Config | [`source-inputs/`](source-inputs/) | Seed URLs and questionnaire metadata. Not a medallion data layer. | Commit-ready. |
| Bronze | [`bronze/raw/rag_pages/`](README.md) | Raw fetched HTML snapshots. | Ignored by git. |
| Silver | [`silver/processed/rag_pages/`](README.md) | Cleaned page text. | Ignored by git. |
| Silver | [`silver/rag/rag_metadata.sqlite`](README.md) | SQLite copy of page/link/chunk metadata. | Ignored by git. |
| Silver | [`silver/datasets/rag_pages.csv`](silver/datasets/rag_pages.csv) | Page manifest, source metadata, drift hashes, and run stamp. | Commit-ready. |
| Silver | [`silver/datasets/rag_links.csv`](silver/datasets/rag_links.csv) | Discovered-link graph, priority scores, crawl decisions, and run stamp. | Commit-ready. |
| Silver | [`silver/datasets/rag_chunks.csv`](silver/datasets/rag_chunks.csv) | Header-aware retrieval chunks, metadata tags, provenance, and run stamp. | Commit-ready. |
| Silver | [`silver/vector_store/chroma/`](README.md) | Local Chroma vector index rebuilt from committed chunks. | Ignored by git. |
| Silver | [`silver/reports/rag_pipeline_report.md`](silver/reports/rag_pipeline_report.md) | Human-readable v1 pipeline report. | Commit-ready. |
| Silver | [`silver/reports/rag_corpus_quality_report.md`](silver/reports/rag_corpus_quality_report.md) | Chunk-quality warnings and cleaning metrics. | Commit-ready. |
| Silver | [`silver/reports/rag_run_manifest.json`](silver/reports/rag_run_manifest.json) | Machine-readable manifest with version, config hashes, artifact hashes, and counts. | Commit-ready. |
| Gold | [`gold/`](gold/) | Reserved for reviewed, release-ready data. | README only for now. |

Gold is intentionally empty in v1. A file should enter Gold only after explicit
team review of Silver outputs.

## Current Corpus

The latest governed v1 run produces:

```text
Pages: 500
Links: 22,727
Chunks: 4,228
Categories: 11
Pipeline version: 1.0.0
Embedding model: sentence-transformers/all-MiniLM-L6-v2
```

The run manifest is the source of truth for exact run ID, artifact hashes, and
configuration hashes.

## Workflow

```text
source-inputs/rag_seed_urls.csv
  -> crawl official pages and approved sublinks
  -> bronze/raw/rag_pages/*.html.gz
  -> silver/processed/rag_pages/*.txt
  -> silver/datasets/rag_pages.csv
  -> silver/datasets/rag_links.csv
  -> silver/datasets/rag_chunks.csv
  -> silver/rag/rag_metadata.sqlite
  -> silver/vector_store/chroma/
  -> silver/reports/rag_pipeline_report.md
  -> silver/reports/rag_corpus_quality_report.md
  -> silver/reports/rag_run_manifest.json
```

The committed CSV outputs are the reviewable source of truth. Chroma is rebuilt
from [`silver/datasets/rag_chunks.csv`](silver/datasets/rag_chunks.csv); SQLite, raw HTML, and clean text are local debug/runtime artifacts.

## Version Governance

Every page, link, and chunk row carries:

- `pipeline_version`
- `pipeline_run_id`
- `artifact_schema_version`
- `generated_at`
- `questionnaire_metadata_version`
- `seed_config_hash`
- `questionnaire_config_hash`
- `crawl_config_hash`
- `chunking_config_version`
- `link_priority_config_version`
- `embedding_model`

[`silver/reports/rag_run_manifest.json`](silver/reports/rag_run_manifest.json) verifies that the CSVs, SQLite DB, reports,
and vector store belong to the same generated corpus after a local rebuild.

## Commands

Build or refresh the v1 local RAG corpus:

```bash
uv run python scripts/data/build_rag_corpus.py --force-rechunk
```

Refresh only metadata and version stamps without recrawling websites:

```bash
uv run python scripts/data/build_rag_corpus.py --metadata-only
```

Validate the corpus:

```bash
uv run python scripts/data/validate_rag_corpus.py
```

Run a local retrieval smoke query:

```bash
uv run python scripts/data/query_rag_corpus.py \
  --query "How do I know what health insurance covers?" \
  --category-id insurance \
  --need-type costs_coverage
```

## Policy

- Bronze is unprocessed source capture.
- Silver is processed/generated and queryable, but not manually approved as
  final recommendation data.
- Gold is reserved for reviewed, release-ready outputs.
- Recommendations must cite official sources and preserve source terms metadata.
- The response layer must apply safety rules before showing user-facing advice.
