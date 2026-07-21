# Project Decision Log

This file records product and engineering decisions that affect shared data contracts, retrieval behavior, and merge readiness.

## 2026-06-24 - Accept the v1 Silver RAG corpus as the Issue #1 direction

Decision: use the `data/rag-pipeline-v1` branch as the replacement direction for the older curated service-record branch.

Reason: the project needs source-backed chunks that can support filtered retrieval and grounded response generation, not a static directory that mostly points users to websites.

Impact: Issue #1 can close after the pre-merge cleanup is complete, validation passes, and the refreshed generated artifacts are internally consistent.

## 2026-06-24 - Treat the depth-3 crawl as the current Silver corpus

Decision: keep the larger crawl as the current Silver exploratory corpus for MVP development.

Reason: the corpus reaches the target scale for the milestone and gives Issues #4 and #5 enough source evidence to test retrieval. It also creates more review burden, so quality reporting is required before merge.

Impact: the corpus is queryable Silver data, not reviewed Gold recommendation data.

## 2026-06-24 - Rebuild Chroma from committed [`rag_chunks.csv`](../../data/silver/datasets/rag_chunks.csv)

Decision: do not commit [`data/silver/vector_store/chroma/`](../../data/README.md). Rebuild it during deployment/startup from the committed [`data/silver/datasets/rag_chunks.csv`](../../data/silver/datasets/rag_chunks.csv).

Reason: Chroma is a generated runtime index and may not be byte-for-byte reproducible. The reviewable source of truth is the committed chunk CSV plus config and manifest.

Impact: deployment/startup must include a Chroma rebuild step. Validation should check functional consistency after rebuild.

## 2026-06-24 - Keep Gold empty until explicit review

Decision: do not create a Gold approved retrieval subset in this PR.

Reason: Issue #1 is about building the RAG corpus pipeline. Gold approval is a later review workflow.

Impact: future RAG-backed app flows may use Silver only with clear wording that Silver chunks are unreviewed and not final recommendation data.

## 2026-06-24 - Safety urgent is guardrail-first

Decision: `safety_urgent` should be treated as guardrail behavior, not as an ordinary recommendation category for this PR.

Reason: urgent safety issues are outside the normal navigator recommendation flow. The app should redirect users to official emergency/crisis resources instead of ranking them like normal service matches.

Impact: emergency-like source chunks can exist for safe redirection, but they should not drive ordinary recommendation ranking.

## 2026-06-24 - Defer ODHF/facility data

Decision: ODHF/facility data is deferred unless nearby-care navigation becomes part of the MVP.

Reason: PR #17 is a web-source RAG corpus. It does not add structured facility names, addresses, coordinates, or distance logic.

Impact: the current MVP should focus on source-backed next-step guidance. Map-like nearby facility navigation is a later source expansion.

## 2026-06-24 - Treat `risk_level` as topic sensitivity, not actual chunk risk

Decision: keep `risk_level` for this PR if renaming is not low-risk, but document that it currently means inherited topic sensitivity.

Reason: many chunks are marked `high_risk` because their category is tax, finances, immigration, insurance, health care, or mental health. That does not mean each chunk is urgent, unsafe, or out of scope.

Impact: future work should either rename this concept to `topic_sensitivity` and derive it from the taxonomy, or remove it from the corpus and let app logic maintain the sensitive-topic list directly.

## 2026-07-19 - Use FastAPI and React/Vite as the active web architecture

Decision: replace the placeholder Streamlit delivery path with a versioned
FastAPI backend and a responsive React/Vite frontend. Production serves the
compiled frontend and API from one container and one origin.

Reason: the API contract can support the web application now and a future
mobile client without duplicating retrieval, safety, or maintenance logic. A
single-origin deployment also reduces production CORS and operational
complexity.

Impact: Streamlit is no longer the active interface direction. The public v1
intake is structured-first with one optional short, non-persistent query; expensive retrieval resources are reused per
process, Chroma is built from committed chunks during image construction, and
all clients must preserve emergency-first routing and safe error responses.


## 2026-07-21 - Share one ranked evidence and LLM response pipeline

Decision: the CLI LLM path and FastAPI recommendation endpoint use one pipeline
with the same defaults: retrieve 21 vector candidates, retain up to 15 approved
chunks, group by normalized canonical page/service into up to 3 distinct
options, use up to 5 chunks per option, and validate all model-cited source IDs
and URLs.

Reason: a retrieved chunk is evidence, not a standalone service recommendation.
Grouping evidence before response writing prevents multiple cards for the same
page and keeps CLI and web ranking, evidence use, and user-facing wording
aligned.

Impact: React renders the validated structured response as cards while the CLI
renders the same response as Markdown. If the model is unavailable, both clients
fall back to the same distinct grouped options.

## 2026-07-21 - Use contextual source authority

Decision: rank the responsible official source for the requested service or decision first, rather than applying one global publisher order. Within an equal contextual authority tier, semantic distance precedes freshness and stable tie-breakers.

Reason: McGill is authoritative for McGill services, while government, public-system, or plan-administrator sources are authoritative for the decisions they own. A global hierarchy can incorrectly bury the responsible source.

Impact: ranking receives category and jurisdiction context, remains deterministic, and cannot use intake jurisdiction as a professional or legal determination.

## 2026-07-21 - Enforce guardrails at input, evidence, and response boundaries

Decision: normalize and screen optional text before retrieval, screen retrieved evidence before display or model use, and validate every model-cited source ID and URL against approved evidence. Governed limitation wording is injected by code.

Reason: domain privacy and prompt-injection risks occur at more than one boundary. Model instructions alone cannot enforce privacy, citation, or limitation contracts.

Impact: emergency routing retains precedence; unsafe requests fail before Chroma or the model; rejected evidence is excluded; and provider or validation failures use a generic grounded fallback.

## 2026-07-21 - Sign and atomically prepare runtime artifacts

Decision: derive ignored SQLite and Chroma artifacts in temporary sibling paths, bind both to the exact governed corpus signature, validate them, and replace active artifacts only after success.

Reason: an interrupted rebuild must not destroy the last valid runtime or combine an index with the wrong chunk corpus.

Impact: readiness verifies counts and signatures. Runtime preparation never restamps or recrawls committed source artifacts.

## 2026-07-21 - Use privacy-safe structured operational logs

Decision: emit JSON Lines using a strict field allowlist and exclude intake text, source bodies, prompts, responses, and identifiers.

Reason: operational diagnosis needs correlation, status, timing, stage, and exception class?not student-authored or retrieved content.

Impact: API responses receive request IDs, failures remain diagnosable, and logs stay within the product privacy boundary.

## 2026-07-21 - Adopt the fixed evaluation package as an Issue 8 baseline

Decision: version the labeled scenario set and deterministic evaluator now, while keeping the participant usability study in Issue 8.

Reason: fixed expected categories, service types, pass rules, safety outcomes, and artifact signatures make regressions reproducible without claiming that automated checks prove usability.

Impact: Issue 7 can verify integration safety and relevance consistently; Issue 8 remains responsible for final scenario results, remediation, and at least five participant sessions.
