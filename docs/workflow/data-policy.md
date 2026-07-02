# Data Policy

The active data layer is the v1 local RAG corpus. The project no longer keeps
the previous static record artifacts in the repository.

## Medallion Policy

- Bronze stores unprocessed source capture: [`data/bronze/raw/rag_pages/`](../../data/README.md).
- Silver stores processed/generated RAG outputs: [`data/silver/processed/`](../../data/README.md),
  [`data/silver/datasets/`](../../data/silver/datasets/), [`data/silver/rag/`](../../data/README.md),
  [`data/silver/vector_store/`](../../data/README.md), and [`data/silver/reports/`](../../data/silver/reports/).
- Gold is reserved for reviewed, release-ready data: [`data/gold/`](../../data/gold/). The current
  version has no Gold dataset.
- [`data/source-inputs/`](../../data/source-inputs/) is configuration, not a medallion data layer.

## Source Policy

- Recommendations must cite official source links.
- Chunks must preserve canonical source URL, section heading, retrieval time,
  source-updated time where available, source terms, and taxonomy metadata.
- Chunks must preserve source group, source owner, source priority rank,
  freshness score, `terms_url`, and `licence_or_terms`.
- Retrieval should prefer primary source groups in this order for same-topic
  evidence: Canada, Quebec, official healthcare systems, McGill, then other
  approved sources.
- Within the same source tier, retrieval should prefer fresher source-updated
  dates when available.
- The response layer must not convert retrieved chunks into medical, legal,
  immigration, tax, insurance, financial, or eligibility decisions.

## Version Policy

Every active Silver row must include:

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

[`data/silver/reports/rag_run_manifest.json`](../../data/silver/reports/rag_run_manifest.json) must match the generated CSVs,
SQLite DB, report, and vector store count. Validation fails if the manifest and
artifacts disagree.

## Storage Policy

- Bronze raw HTML, Silver cleaned page text, Silver SQLite files, and Silver
  Chroma indexes are generated locally and ignored by git. Chroma must be rebuilt
  from committed [`data/silver/datasets/rag_chunks.csv`](../../data/silver/datasets/rag_chunks.csv) during deployment/startup.
- [`data/silver/datasets/rag_pages.csv`](../../data/silver/datasets/rag_pages.csv),
  [`data/silver/datasets/rag_links.csv`](../../data/silver/datasets/rag_links.csv),
  [`data/silver/datasets/rag_chunks.csv`](../../data/silver/datasets/rag_chunks.csv),
  [`data/silver/reports/rag_pipeline_report.md`](../../data/silver/reports/rag_pipeline_report.md),
  [`data/silver/reports/rag_corpus_quality_report.md`](../../data/silver/reports/rag_corpus_quality_report.md), and
  [`data/silver/reports/rag_run_manifest.json`](../../data/silver/reports/rag_run_manifest.json) are reviewable Silver artifacts.
- Do not store sensitive personal identifiers or detailed health descriptions.
- Do not use user-specific browsing at answer time.

## Change Policy

Changes to taxonomy, RAG metadata fields, source authority, questionnaire stable
IDs, crawl rules, chunking logic, link-priority logic, embedding model, or
retrieval filters require pull-request review.
