# Architecture

McGill Care Compass is a source-grounded navigator. The active v1 architecture
uses a local RAG data layer, deterministic intake filters, guarded retrieval,
and optional LLM response writing over approved evidence.

## Subsystems

1. **Source configuration**: [`data/source-inputs/rag_seed_urls.csv`](../../data/source-inputs/rag_seed_urls.csv) and
   [`data/source-inputs/questionnaire_metadata_map.yml`](../../data/source-inputs/questionnaire_metadata_map.yml).
2. **RAG ingestion**: [`scripts/data/build_rag_corpus.py`](../../scripts/data/build_rag_corpus.py) crawls official pages,
   saves raw and cleaned content, chunks pages, tags metadata, embeds locally,
   and writes Chroma.
3. **Validation and governance**: [`scripts/data/validate_rag_corpus.py`](../../scripts/data/validate_rag_corpus.py) checks
   schema, committed CSV hashes, manifest consistency, report presence, and SQLite
   table parity. The runtime health command separately validates the complete
   vector-store corpus signature.
4. **Structured intake**: the terminal demo collects category, need type, student context,
   jurisdiction, language, urgency, route context, and optional free-text query.
   The Streamlit shell is retained as a placeholder and is not the active Issue 6 path.
5. **Retrieval**: after adversarial inspection and emergency precedence, the terminal app
   filters chunks using questionnaire metadata, retrieves
   up to 21 vector candidates, then ranks by source authority, semantic relevance, and
   freshness before capping approved evidence for display or response writing.
6. **Response layer**: deterministic formatting remains the fallback. The optional
   Responses API layer groups approved evidence into at most three user-facing options,
   uses up to five chunks per option, validates cited source IDs, discloses conflicts,
   validates that every displayed URL belongs to the cited evidence, and deterministically
   enforces high-risk limitation wording.
7. **Operational safety**: the CLI application boundary converts missing/stale Chroma and
   unexpected retrieval exceptions into a source-linked `system_error` response. Structured
   logs contain only bounded operational fields, never query or identifier values.
8. **Maintenance and health**: read-only CLI checks report artifact/signature parity, source
   freshness, failed fetches, skipped links, missing metadata, category coverage, and chunk
   quality. Runtime preparation rebuilds ignored SQLite and Chroma artifacts from tracked CSVs.
9. **Evaluation**: the versioned fixed scenario set runs deterministic relevance, source-link,
   limitation, emergency, unsupported, empty, low-confidence, system-error, instruction-
   override, prompt-extraction, source-fabrication, role-manipulation, sensitive-identifier,
   retrieved prompt-injection, and benign pass-through checks.

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
  -> evidence grouping and source validation
  -> deterministic or optional LLM-written source-grounded response
  -> fixed-scenario evaluation reports
```

## Design Principles

- Prefer official sources and preserve source terms.
- Keep source capture, processed chunks, and reviewed outputs separate.
- Use deterministic metadata and filters before semantic retrieval.
- Keep the vector index rebuildable from committed Silver chunk data.
- Treat high-risk topics as navigation, not professional advice.
- Keep intentionally skipped crawl links separate from actual failed page fetches.
- Log exception types and bounded routing state without user-authored text or identifiers.
- Require a reviewed Gold dataset before claiming release-ready recommendation
  data.
