# RAG Data Pipeline Report

Generated: `2026-06-24T07:52:50+00:00`

## Summary

| Metric | Value |
| --- | ---: |
| Pages processed | 490 |
| Links recorded | 22,548 |
| Header-aware chunks | 4,239 |
| Vector store status | `rebuilt:4239` |
| Max crawl depth | 3 |
| Max pages | 500 |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |

Pipeline v1 crawls approved official pages, stores raw and cleaned source content, builds header-aware chunks, tags chunks with questionnaire metadata, embeds locally, and writes a rebuildable Chroma index. The current run is Silver: processed and queryable, but not manually reviewed as Gold recommendation data.

## Data Flow

```text
data/source-inputs/rag_seed_urls.csv
  -> crawl approved pages and sublinks
  -> data/bronze/raw/rag_pages/*.html.gz
  -> data/silver/processed/rag_pages/*.txt
  -> data/silver/datasets/rag_pages.csv
  -> data/silver/datasets/rag_links.csv
  -> data/silver/datasets/rag_chunks.csv
  -> data/silver/rag/rag_metadata.sqlite
  -> data/silver/vector_store/chroma/
```

Tracked CSVs and the run manifest are the durable review layer. SQLite, cleaned text, Bronze HTML, and Chroma are local rebuildable outputs.

## Coverage

| Category ID | Chunks |
| --- | ---: |
| `academics` | 199 |
| `documents_admin` | 55 |
| `finances` | 657 |
| `health_care` | 350 |
| `housing` | 88 |
| `immigration_status` | 402 |
| `insurance` | 90 |
| `language_integration` | 2 |
| `mental_health` | 435 |
| `tax` | 1,605 |
| `work_career` | 356 |

Source groups: Canada 1,605 chunks, McGill 2,355 chunks, Quebec 279 chunks.

## Governance

- Pipeline version: `1.0.0`
- Pipeline run ID: `20260624T074008Z`
- Artifact schema version: `2`
- Questionnaire metadata version: `2`
- Run manifest: `data/silver/reports/rag_run_manifest.json`
- Drift status: 121 changed, 4 fetch failed, 4 new, 361 unchanged.

Retrieval reranking prefers primary source groups in this order: Canada, Quebec, official healthcare systems, McGill, then other approved sources. Freshness uses source-modified dates when available, otherwise retrieval time.

## Commands

```powershell
uv run python scripts/data/build_rag_corpus.py
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/data/query_rag_corpus.py --query "How do I access health insurance?" --category-id insurance --need-type costs_coverage
```

Use `--metadata-only` after questionnaire mapping changes when the page crawl does not need to be refreshed.
