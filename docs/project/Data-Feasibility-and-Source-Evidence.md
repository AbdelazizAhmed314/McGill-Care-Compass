# Data Feasibility and Source Evidence

## Purpose

This document summarizes the evidence that McGill Care Compass has enough
official source material to support a source-grounded navigator. The active data
evidence is the v1 local RAG corpus.

Primary evidence:

- [data/README.md](../../data/README.md)
- [rag_pipeline_report.md](../../data/silver/reports/rag_pipeline_report.md)
- [rag_run_manifest.json](../../data/silver/reports/rag_run_manifest.json)
- [rag-data-pipeline.md](../workflow/rag-data-pipeline.md)

## Main Finding

Official McGill, Canada, and Quebec pages provide enough accessible content to
build a practical navigator. The v1 pipeline turns those pages into
source-grounded chunks that can support filtered retrieval and cited next-step
responses.

The implementation challenge is no longer finding source pages. It is keeping
the corpus relevant, versioned, auditable, and safe for high-risk navigation.

## Current Evidence

| Evidence item | Current v1 result | Interpretation |
| --- | ---: | --- |
| Active seed URLs | 21 | The source universe is explicit and reproducible. |
| Pages processed | 500 | The crawler reaches the configured page target under depth and source-scope limits. |
| Discovered links recorded | 22,727 | The pipeline preserves crawl decisions and skipped links for review. |
| Header-aware chunks | 4,228 | The corpus contains retrievable, section-aware source text. |
| Categories covered | 11 | The corpus covers the locked taxonomy categories needed for the MVP. |
| Vector count | 4,228 | Chroma contains one vector per active chunk. |
| Pipeline version | 1.0.0 | Generated artifacts are tied to a versioned pipeline run. |

## Source Layers

| Layer | Role | Can power recommendations? |
| --- | --- | --- |
| Bronze raw HTML | Exact fetched source snapshots. | No. Used for traceability and drift checks. |
| Silver clean text | Boilerplate-removed source text. | No. Used to rebuild chunks. |
| Silver page/link manifests | Crawl evidence, source metadata, link decisions, and drift state. | No. Used for audit and maintenance. |
| Silver chunks | Header-aware source snippets with questionnaire metadata and provenance. | Yes, through filtered retrieval. |
| Silver Chroma index | Local vector search over active chunks. | Yes, but only with source filters and safety rules. |
| Gold reviewed data | Future release-ready recommendation artifacts. | Not available in v1. |

## Why The v1 RAG Corpus Is Feasible

The v1 pipeline addresses the team's main data concern: the app should not only
point users to websites. It extracts useful page content into chunks with
headings, source links, nearby links, category metadata, need-type tags, and
source terms. The response layer can use those chunks to summarize next steps,
contacts, costs, required documents, and eligibility-adjacent information while
citing official sources.

The corpus remains maintainable because each run records source hashes,
configuration hashes, pipeline version, artifact hashes, and row counts. When a
website changes, the next run can detect the changed clean-text hash and refresh
the affected chunks and vectors.

## Architecture Assumptions

- v1 ingests official HTML pages from McGill, Canada, and Quebec sources.
- PDFs, login-gated pages, JavaScript-only pages, and irrelevant external links
  are logged but not ingested.
- The crawler follows only approved domains and path prefixes.
- The pipeline uses local/open-source tooling and
  `sentence-transformers/all-MiniLM-L6-v2`.
- The questionnaire metadata map is the shared contract with Mustafa's intake
  flow.
- Silver outputs are generated and queryable, but not yet manually approved as
  final Gold recommendation data.

## Limits

The evidence does not support:

- a free-form advice chatbot;
- medical, legal, immigration, tax, insurance, financial, or eligibility
  decisions;
- guarantees about service availability, wait times, costs, or eligibility;
- retrieval from unapproved external pages;
- treating Silver outputs as reviewed Gold data.

The pipeline can still ingest noisy in-scope pages when official sites expose
large navigation surfaces. The link-priority score and reasons make that visible
for review and tuning.

## Implementation Implications

The app should:

- filter chunks by questionnaire metadata before semantic search;
- prefer primary sources in the configured order: Canada, Quebec, official
  healthcare systems, McGill, then other approved sources;
- show citations and source dates;
- surface source terms metadata where needed;
- use high-risk guardrails before producing final wording;
- promote only reviewed subsets of Silver data to Gold.
