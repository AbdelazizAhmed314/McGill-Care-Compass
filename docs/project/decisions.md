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

## 2026-06-24 - Rebuild Chroma from committed `rag_chunks.csv`

Decision: do not commit `data/silver/vector_store/chroma/`. Rebuild it during deployment/startup from the committed `data/silver/datasets/rag_chunks.csv`.

Reason: Chroma is a generated runtime index and may not be byte-for-byte reproducible. The reviewable source of truth is the committed chunk CSV plus config and manifest.

Impact: deployment/startup must include a Chroma rebuild step. Validation should check functional consistency after rebuild.

## 2026-06-24 - Keep Gold empty until explicit review

Decision: do not create a Gold approved retrieval subset in this PR.

Reason: Issue #1 is about building the RAG corpus pipeline. Gold approval is a later review workflow.

Impact: app prototypes may use Silver only with clear wording that Silver chunks are unreviewed and not final recommendation data.

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
