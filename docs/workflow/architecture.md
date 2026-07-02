# Architecture

McGill Care Compass is a source-grounded navigator. The active v1 architecture
uses a local RAG data layer, deterministic intake filters, and guarded
recommendation generation.

## Subsystems

1. **Source configuration**: [`data/source-inputs/rag_seed_urls.csv`](../../data/source-inputs/rag_seed_urls.csv) and
   [`data/source-inputs/questionnaire_metadata_map.yml`](../../data/source-inputs/questionnaire_metadata_map.yml).
2. **RAG ingestion**: [`scripts/data/build_rag_corpus.py`](../../scripts/data/build_rag_corpus.py) crawls official pages,
   saves raw and cleaned content, chunks pages, tags metadata, embeds locally,
   and writes Chroma.
3. **Validation and governance**: [`scripts/data/validate_rag_corpus.py`](../../scripts/data/validate_rag_corpus.py) checks
   schema, artifact hashes, manifest consistency, SQLite parity, and vector
   count.
4. **Structured intake**: the UI collects category, need type, student context,
   jurisdiction, language, urgency, and delivery preferences.
5. **Retrieval**: the app filters chunks using questionnaire metadata, then runs
   semantic search inside the filtered subset.
6. **Response layer**: the app summarizes retrieved chunks into next steps,
   contacts, documents, costs, and citations while applying high-risk safety
   rules.
7. **Evaluation**: fixed scenarios test retrieval relevance, source grounding,
   refusal/deferral behavior, and usability.

## Data Flow

```text
official seed URLs
  -> crawl and link ranking
  -> Bronze raw HTML
  -> Silver clean text
  -> Silver pages/links/chunks CSVs
  -> Silver SQLite metadata
  -> Silver Chroma vector index
  -> filtered retrieval
  -> source-grounded response
```

## Design Principles

- Prefer official sources and preserve source terms.
- Keep source capture, processed chunks, and reviewed outputs separate.
- Use deterministic metadata and filters before semantic retrieval.
- Keep the vector index rebuildable from committed Silver chunk data.
- Treat high-risk topics as navigation, not professional advice.
- Require a reviewed Gold dataset before claiming release-ready recommendation
  data.
