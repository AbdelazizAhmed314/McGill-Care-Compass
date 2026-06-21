# RAG Data Pipeline Report

Generated: `2026-06-21T19:54:18+00:00`

## Summary

- Pages processed: **500**
- Links recorded: **22727**
- Header-aware chunks: **4228**
- Vector store status: `rebuilt:4228`
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

```text
data/source-inputs/rag_seed_urls.csv
  -> crawl official pages and approved sublinks
  -> data/bronze/raw/rag_pages/*.html.gz
  -> data/silver/processed/rag_pages/*.txt
  -> data/silver/datasets/rag_pages.csv
  -> data/silver/datasets/rag_links.csv
  -> data/silver/datasets/rag_chunks.csv
  -> data/silver/rag/rag_metadata.sqlite
  -> data/silver/vector_store/chroma/
```

The CSV and SQLite files are the durable reproducible data layer. Chroma is a
local rebuildable index created from `rag_chunks.csv`.

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
- `data/source-inputs/questionnaire_metadata_map.yml` is the shared contract with
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
- Pipeline run ID: `20260621T195343Z`
- Artifact schema version: `1`
- Questionnaire metadata version: `2`
- Seed config hash: `a2858cb02a78ac24c244efe1f4b6b9a7cdc7801c914c1381a1917f1fd12ec3b8`
- Questionnaire config hash: `1414b763f53deab28100010b2e51dbeffdcae719d1bd4485d04d9d4faea4ead4`
- Crawl config hash: `2c774104781ff52e68c13b6dd36cb1048005621267e6632b8e4a11134b85e9f3`
- Chunking config version: `1`
- Link priority config version: `1`
- Run manifest: `data/silver/reports/rag_run_manifest.json`

## Drift Status

- fetch_failed: **4**
- new: **337**
- unchanged: **159**

## Link Types

- external: **2577**
- file: **192**
- in_scope: **11776**
- skipped: **8080**
- tel: **102**

## Link Crawl Decisions

- not_crawled: **22248**
- queued: **479**

## Chunk Coverage

| Category | Chunks |
| --- | ---: |
| `academics` | 199 |
| `documents_admin` | 55 |
| `finances` | 657 |
| `health_care` | 335 |
| `housing` | 91 |
| `immigration_status` | 402 |
| `insurance` | 90 |
| `language_integration` | 2 |
| `mental_health` | 435 |
| `tax` | 1582 |
| `work_career` | 380 |

## Source Ranking

Retrieval reranking prefers primary source groups in this order:
Canada, Quebec, official healthcare systems, McGill, then other approved sources.
Freshness is scored from source-modified dates when available, otherwise retrieval time.

| Source group | Chunks |
| --- | ---: |
| `canada` | 1582 |
| `mcgill` | 2382 |
| `quebec` | 264 |

## Persistent Outputs

- Bronze raw HTML: `data/bronze/raw/rag_pages/`
- Silver clean text: `data/silver/processed/rag_pages/`
- Silver SQLite metadata: `data/silver/rag/rag_metadata.sqlite`
- Silver page CSV: `data/silver/datasets/rag_pages.csv`
- Silver link CSV: `data/silver/datasets/rag_links.csv`
- Silver chunk CSV: `data/silver/datasets/rag_chunks.csv`
- Silver Chroma vector DB: `data/silver/vector_store/chroma/`

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

- The vector database is rebuildable from `rag_chunks.csv`.
- Questionnaire wording changes should update `data/source-inputs/questionnaire_metadata_map.yml`
  and rerun with `--metadata-only`; this refreshes chunk metadata without recrawling pages.
- Website content changes are detected through clean-text hashes and reflected in `drift_status`.
