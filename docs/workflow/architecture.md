# Architecture

McGill Care Compass is a source-grounded navigator. The active v1 web
architecture uses a React/Vite interface, a versioned FastAPI backend,
deterministic guardrails, filtered retrieval, and a governed local RAG layer.

## Subsystems

1. **Web interface**: `web/` provides a responsive structured intake,
   recommendation states, emergency-first presentation, and an internal status
   view. It does not collect open-ended text or sensitive identifiers.
2. **Versioned API**: `src/mcgill_care_compass/api/` exposes liveness,
   readiness, intake options, recommendations, and a read-only maintenance
   report under `/api/v1`.
3. **Source configuration**:
   `data/source-inputs/rag_seed_urls.csv` and
   `data/source-inputs/questionnaire_metadata_map.yml`.
4. **RAG ingestion**: `scripts/data/build_rag_corpus.py` crawls official
   pages, saves local raw and cleaned content, chunks pages, tags metadata, and
   writes reviewable Silver artifacts.
5. **Validation and governance**:
   `scripts/data/validate_rag_corpus.py` validates committed corpus artifacts
   by default. Ignored SQLite and Chroma artifacts are optional unless strict
   local-artifact validation is requested.
6. **Guarded retrieval**: emergency and unsupported requests return before
   loading Chroma or the embedding model. Supported requests use deterministic
   metadata filters, semantic retrieval, evidence-quality checks, and ranked
   source chunks.
7. **Runtime resources**: the API lazily loads and reuses one embedding model
   and one Chroma collection per process. Production uses one worker to avoid
   duplicating model memory.
8. **Maintenance and health**: maintenance reporting covers freshness, broken
   links, missing data, and category coverage. Separate liveness and readiness
   endpoints keep a process check distinct from retrieval readiness.
9. **Deployment**: the Docker build compiles React, prepares Chroma from the
   committed chunk CSV, runs strict readiness checks, and serves the frontend
   and API from one origin.

## Request Flow

```text
React structured intake
  -> POST /api/v1/recommendations
  -> schema and privacy validation
  -> emergency / unsupported guardrails
  -> cached embedding model and Chroma collection
  -> filtered retrieval and deterministic ranking
  -> evidence-quality gate
  -> safe API response state
  -> React result, fallback, or emergency component
```

## Data Flow

```text
official seed URLs
  -> crawl and link ranking
  -> Bronze raw HTML
  -> Silver clean text
  -> committed Silver pages/links/chunks CSVs
  -> deployment-time Chroma rebuild
  -> FastAPI retrieval runtime
  -> source-grounded web response
```

## Deployment Topology

Local development uses Vite on port 5173 and FastAPI on port 8000. Vite proxies
`/api` to FastAPI.

Production uses one container and one origin:

```text
browser or future mobile client
  -> FastAPI /api/v1
  -> retrieval runtime

browser
  -> FastAPI static hosting
  -> compiled React application
```

A future mobile client can reuse the same `/api/v1` contract without moving
safety or retrieval rules into the client.

## Design Principles

- Prefer official sources and preserve source terms.
- Keep public intake structured and exclude sensitive identifiers.
- Apply emergency and unsupported routing before model/vector access.
- Keep source capture, processed chunks, and reviewed outputs separate.
- Keep Chroma rebuildable from committed Silver chunk data.
- Never expose raw exception text or rejected intake values.
- Treat high-risk topics as navigation, not professional advice.
- Require reviewed Gold data before claiming release-ready recommendation data.
