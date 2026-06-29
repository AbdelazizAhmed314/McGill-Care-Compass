# Safety And Evaluation

This document is the source of truth for safety boundaries, source authority, evaluation targets, and usability checks.

## Core Safety Position

McGill Care Compass routes students to official starting points. It does not diagnose, assess emergency severity, decide eligibility, interpret medical, legal, immigration, tax, insurance, or financial status, or replace a qualified advisor.

## Source Authority Rules

Rank sources by authority before convenience:

1. Emergency or immediate-safety instructions first when the intake suggests danger.
2. McGill-owned student services first for McGill-owned needs.
3. Quebec, Canada, RAMQ, CRA, IRCC, official healthcare, or McGill sources first for high-risk topics.
4. Community sources only when they are relevant, source-linked, and not making official eligibility claims.

When two sources have equal authority, break ties by specificity to the student situation, accessibility or location, source freshness, then stable record or chunk ID.

## High-Risk Topic Boundaries

| Topic | The navigator may do | The navigator must not do |
| --- | --- | --- |
| Medical and mental health | Route to official care access, crisis, 811, Wellness Hub, or emergency resources. | Diagnose, triage symptoms, recommend treatment, or decide whether a condition is an emergency. |
| Immigration and legal | Link to official McGill, Quebec, Canada, or legal-support starting points. | Interpret status, decide permit eligibility, or provide legal advice. |
| Tax and finances | Link to official CRA, McGill aid, and trusted support resources. | Decide tax residency, benefit eligibility, financial aid eligibility, or filing obligations. |
| Insurance | Explain where official coverage information lives and what source to check. | Decide coverage, claims, reimbursement, or eligibility. |
| Unsupported requests | Explain that the navigator cannot safely answer and point to official help. | Invent an answer or use weak source evidence. |

## Guardrail Behavior

- `safety_urgent` is guardrail behavior, not an ordinary recommendation category.
- Emergency-like inputs should bypass normal ranking and show urgent official resources first.
- Silver RAG chunks are evidence candidates, not reviewed Gold advice.
- User-facing answers must show official links, source context, and limitation wording.
- The app should not collect student ID, SIN, passport number, medical record number, claim numbers, diagnosis, symptom narrative, immigration-document details, or detailed finances.

## Evaluation Target

The recommendation-quality target is:

> At least 90% of fixed, labeled student scenarios return a relevant service or source in the top three recommendations.

A top-three result is relevant only if it matches the scenario category, fits the student context, includes an official source link, and does not violate the safety boundary.

## Scenario Coverage

The fixed evaluation set should cover:

- ordinary newcomer navigation;
- `health_care`, `mental_health`, `insurance`, `immigration_status`, `tax`, `finances`, `work_career`, `housing`, `academics`, `documents_admin`, and `language_integration`;
- urgent or safety-related inputs;
- unsupported requests;
- empty or low-evidence retrieval;
- source-link presence and limitation wording.

## Required Tests

- Unit tests for deterministic guardrails, matching, and explanation behavior.
- Data validation for required RAG fields, source URLs, review status, and metadata consistency.
- Retrieval checks for representative scenarios.
- Negative tests for unsupported requests, high-risk claims, and no-source answers.
- App smoke test from documented setup commands.

## Usability Plan

Run at least five sessions with target or proxy users before the final submission. Record whether each participant can complete the intake, understand the top result, identify an official next step, notice limitations, and finish in under two minutes for common scenarios. Convert findings into prioritized fixes for wording, layout, data coverage, and matching.

## Acceptance Criteria

- Safety wording appears for medical, mental health, immigration, legal, tax, financial, insurance, and eligibility-sensitive cases.
- Every recommendation cites at least one official source URL or fails safely.
- The top-three evaluation target is met or failures are documented with owners.
- Usability findings are summarized and critical issues are resolved or explicitly deferred.
