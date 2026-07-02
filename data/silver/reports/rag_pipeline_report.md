# RAG Data Pipeline Report

Generated: `2026-06-24T07:52:50+00:00`

## Summary

- Pages processed: **490**
- Links recorded: **22548**
- Header-aware chunks: **4239**
- Vector store status: `rebuilt:4239`
- Max crawl depth: **3**
- Max pages: **500**
- Max queued links per page: **10**, relevance-ranked before queueing
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`

## Work Completed

Pipeline v1 replaces the earlier static service-record dataset with a reusable
local RAG ingestion pipeline. It crawls official seed pages, stores raw and
cleaned source content, builds header-aware chunks, tags chunks with the shared
questionnaire metadata contract, embeds locally, and writes a Chroma vector
index for retrieval.

The current run is a Silver dataset. It is processed and queryable, but it has
not been manually reviewed as a final Gold recommendation dataset.

## Architecture

- [`data/source-inputs/rag_seed_urls.csv`](../../source-inputs/rag_seed_urls.csv)
- crawl official pages and approved sublinks
- [`data/bronze/raw/rag_pages/*.html.gz`](../../README.md)
- [`data/silver/processed/rag_pages/*.txt`](../../README.md)
- [`data/silver/datasets/rag_pages.csv`](../datasets/rag_pages.csv)
- [`data/silver/datasets/rag_links.csv`](../datasets/rag_links.csv)
- [`data/silver/datasets/rag_chunks.csv`](../datasets/rag_chunks.csv)
- [`data/silver/rag/rag_metadata.sqlite`](../../README.md)
- [`data/silver/vector_store/chroma/`](../../README.md)

The CSV and SQLite files are the durable reproducible data layer. Chroma is a
local rebuildable index created from [`rag_chunks.csv`](../datasets/rag_chunks.csv).

## Exploration Algorithm

The crawler starts from official seed URLs and explores in-scope sublinks up to
the configured depth and page limits. It canonicalizes URLs, removes tracking
parameters and fragments, deduplicates by canonical URL, and records every
discovered link even when the link is not crawled.

For each page, the crawler ranks in-scope links before queueing. The ranking is
deterministic and favors links whose anchor text, section heading, or path
matches questionnaire terms and service-navigation terms such as eligibility,
documents, cost, coverage, contact, booking, location, and deadlines. It
deprioritizes links that look like news, events, staff pages, calendars, login
pages, social media, or generic navigation. The link audit fields
`link_priority_score`, `link_priority_reasons`, `crawl_decision`, and
`skip_reason` explain each decision.

## Chunking And Metadata Algorithm

The parser removes scripts, navigation, headers, footers, forms, cookie blocks,
and obvious boilerplate. It preserves `h1` to `h4` headings, attaches paragraphs,
lists, and tables to the nearest heading, and prepends the heading path to
`embedding_text` while keeping `chunk_text` clean for citation.

Chunk metadata comes from four places:

- seed configuration: source, taxonomy, authority, terms, jurisdiction, language,
  student type, and crawl limits;
- parsed HTML: page title, section heading, heading path, nearby links, source
  updated date, and content hashes;
- questionnaire metadata map: deterministic need-type tags and boolean filters;
- ranking helper: source priority rank and freshness score.

No LLM assigns metadata in v1.

## Assumptions

- Official McGill, Canada, and Quebec HTML pages are the approved v1 source
  types.
- PDFs, login-gated pages, JavaScript-only pages, and irrelevant external pages
  are logged but not ingested.
- `sentence-transformers/all-MiniLM-L6-v2` is the local embedding model.
- [`data/source-inputs/questionnaire_metadata_map.yml`](../../source-inputs/questionnaire_metadata_map.yml) is the shared contract with
  Mustafa's questionnaire.
- Gold remains empty until the team reviews and approves a subset of Silver
  outputs.

## Limits

- The corpus can contain noisy pages when approved sites expose broad internal
  navigation. The link-priority fields make this visible for later tuning.
- The crawler detects changed page content through hashes, but it does not judge
  whether a changed page improves or weakens an answer.
- The metadata tagger is deterministic keyword and regex logic. It is transparent
  but can miss implied meaning.
- The pipeline stores source-grounded chunks. The response layer must still apply
  safety rules before producing user-facing advice.
- The corpus is English-only in the current run.

## Version Governance

- Pipeline version: `1.0.0`
- Pipeline run ID: `20260624T074008Z`
- Artifact schema version: `2`
- Questionnaire metadata version: `2`
- Seed config hash: `fa0d64b45385a55498aba24cfedd2b16579532eaf36da71e0092f1e00d39c693`
- Questionnaire config hash: `edf7353d73278ef885a30bb447e69e4c7322225769fae824ca4b10a4f9f49345`
- Crawl config hash: `f2c2545c6d452413f90e3e514f74612ad0502847db9cafc5f9c0154c7279933e`
- Chunking config version: `1`
- Link priority config version: `1`
- Run manifest: [`data/silver/reports/rag_run_manifest.json`](rag_run_manifest.json)

## Drift Status

- changed: **121**
- fetch_failed: **4**
- new: **4**
- unchanged: **361**

## Link Types

- external: **2576**
- file: **192**
- in_scope: **11756**
- skipped: **7922**
- tel: **102**

## Link Crawl Decisions

- not_crawled: **22079**
- queued: **469**

## Chunk Coverage

| Category | Chunks |
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
| `tax` | 1605 |
| `work_career` | 356 |

## Source Ranking

Retrieval reranking prefers primary source groups in this order:
Canada, Quebec, official healthcare systems, McGill, then other approved sources.
Freshness is scored from source-modified dates when available, otherwise retrieval time.

| Source group | Chunks |
| --- | ---: |
| `canada` | 1605 |
| `mcgill` | 2355 |
| `quebec` | 279 |

## Persistent Outputs

- Bronze raw HTML: [`data/bronze/raw/rag_pages/`](../../README.md)
- Silver clean text: [`data/silver/processed/rag_pages/`](../../README.md)
- Silver SQLite metadata: [`data/silver/rag/rag_metadata.sqlite`](../../README.md)
- Silver page CSV: [`data/silver/datasets/rag_pages.csv`](../datasets/rag_pages.csv)
- Silver link CSV: [`data/silver/datasets/rag_links.csv`](../datasets/rag_links.csv)
- Silver chunk CSV: [`data/silver/datasets/rag_chunks.csv`](../datasets/rag_chunks.csv)
- Silver Chroma vector DB: [`data/silver/vector_store/chroma/`](../../README.md)
- Silver quality report: [`data/silver/reports/rag_corpus_quality_report.md`](rag_corpus_quality_report.md)

## Rebuild Commands

```bash
uv run python scripts/data/build_rag_corpus.py
uv run python scripts/data/validate_rag_corpus.py
uv run python scripts/data/query_rag_corpus.py \
  --query "How do I access health insurance?" \
  --category-id insurance \
  --need-type costs_coverage
```

## Notes

- The vector database is rebuildable from [`rag_chunks.csv`](../datasets/rag_chunks.csv).
- Questionnaire wording changes should update [`data/source-inputs/questionnaire_metadata_map.yml`](../../source-inputs/questionnaire_metadata_map.yml)
  and rerun with `--metadata-only`; this refreshes chunk metadata without recrawling pages.
- Website content changes are detected through clean-text hashes and reflected in `drift_status`.
