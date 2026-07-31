import { cleanup, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import type { Evidence, IntakeOptions, RecommendationResponse } from "../types"
import { NavigatorForm } from "./NavigatorForm"
import { RecommendationResults } from "./RecommendationResults"

afterEach(cleanup)

const options: IntakeOptions = {
  categories: [{ id: "housing", label: "Housing and basic needs" }],
  need_types: [{ id: "general_navigation", label: "General navigation" }],
  student_types: [{ id: "international_student", label: "International student" }],
  jurisdictions: [{ id: "mcgill", label: "McGill" }],
  urgency_levels: [
    { id: "routine", label: "Routine" },
    { id: "emergency_immediate_danger", label: "Emergency or immediate danger" },
  ],
  languages: [{ id: "en", label: "English" }],
  campus_locations: [{ id: "", label: "No preference" }],
  delivery_preferences: [{ id: "", label: "No preference" }],
}

const developerEvidence = {
  chunk_id: "chunk-1",
  vector_id: "vector-1",
  heading_path: "Housing > Support",
  review_status: "silver_unreviewed",
  label_method: "rules",
  label_confidence: "high",
  distance: 0.1,
  quality_warnings: [],
}

const sharedPresentation = {
  opening_summary: "",
  limitations: [] as string[],
  conflict_disclosure: {
    has_conflict: false,
    what_differs: "",
    why_this_route_was_chosen: "",
    how_to_double_check: "",
    source_ids_considered: [] as string[],
  },
  official_sources: [] as Array<{ label: string; url: string; source_id: string }>,
  generation_mode: "deterministic" as const,
  generation_diagnostics: {
    request_id: "request-test",
    generation_mode: "deterministic" as const,
    model: "gpt-test",
    attempts: 2,
    fallback_reason_code: "unsupported_source_id",
    validation_reason_code: "unsupported_source_id",
    openai_request_id: "req_openai_test",
    openai_response_id: "resp_test",
    timings_ms: { openai_call: 123.4 },
  },
}

const evidence: Evidence = {
  title: "Housing support",
  category_id: "housing",
  category_label: "Housing and basic needs",
  excerpt: "Official source evidence.",
  recommended_next_step: "Open the official source and review the listed contact route.",
  canonical_url: "https://www.mcgill.ca/example",
  source_publisher: "McGill University",
  retrieved_at: "2026-07-01",
  source_updated_at: "2026-06-01",
  last_checked: "2026-07-01",
  review_status: "silver_unreviewed",
  label_confidence: "high",
  distance: 0.1,
  match_reason: "Matched your housing selection.",
  limitation: "Confirm current details with the responsible office.",
  quality_warnings: [],
  source_details: {
    heading_path: "Housing > Support",
    publisher: "McGill University",
    source_group: "mcgill",
    authority_level: "official",
    terms_url: "https://www.mcgill.ca/terms",
    licence_or_terms: "Official site terms",
    retrieved_at: "2026-07-01",
    source_updated_at: "2026-06-01",
  },
  source_ids_used: ["chunk-1"],
  supporting_evidence: [developerEvidence],
  developer_details: developerEvidence,
}

describe("navigator safety contract", () => {
  it("reviews structured choices and an optional short question before submission", async () => {
    const submit = vi.fn().mockResolvedValue(undefined)
    render(<NavigatorForm options={options} busy={false} onSubmit={submit} />)

    const query = screen.getByRole("textbox", { name: /Optional short question/ })
    await userEvent.type(query, "Where can I learn about tenant rights?")
    await userEvent.selectOptions(screen.getByLabelText("Main need"), "housing")
    await userEvent.click(screen.getByRole("button", { name: "Review choices" }))

    expect(submit).not.toHaveBeenCalled()
    expect(screen.getByRole("heading", { name: "Check your choices" })).toBeVisible()
    expect(screen.getByText("Where can I learn about tenant rights?")).toBeVisible()

    await userEvent.click(screen.getByRole("button", { name: "Find official starting points" }))
    expect(submit).toHaveBeenCalledWith(
      expect.objectContaining({
        category_id: "housing",
        urgency_level: "routine",
        query: "Where can I learn about tenant rights?",
      }),
    )
  })

  it("hides developer evidence until developer mode is enabled", async () => {
    const response: RecommendationResponse = {
      ...sharedPresentation,
      opening_summary: "Start with the official housing support route.",
      limitations: ["Confirm current details with the responsible office."],
      generation_mode: "llm",
      status: "matched",
      matched_filters: { category_id: "housing" },
      relaxed_level: 0,
      primary_result: evidence,
      backup_results: [],
      emergency_resources: [],
      safety_notice: null,
      limitation_notice: "This is navigation support.",
      message: "",
      error_code: "",
      intake_summary: [{ label: "Main need", value: "Housing and basic needs" }],
    }

    render(<RecommendationResults result={response} onStartOver={vi.fn()} />)

    expect(screen.getByText("Start with the official housing support route.")).toBeVisible()
    expect(
      screen.getByRole("status", { name: "Response generation: Responses API" }),
    ).toBeVisible()
    expect(screen.getByText("Recommended next step")).toBeVisible()
    expect(
      screen.getAllByText("Confirm current details with the responsible office.").length,
    ).toBeGreaterThan(0)
    expect(screen.queryByText("chunk-1")).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Developer mode: Off" }))
    expect(screen.getAllByText("chunk-1").length).toBeGreaterThan(0)
    expect(screen.getByText("llm")).toBeVisible()
    expect(screen.getByText("request-test")).toBeVisible()
    expect(screen.getAllByText("unsupported_source_id").length).toBeGreaterThan(0)
    expect(screen.getByText("req_openai_test")).toBeVisible()
    expect(screen.getByRole("button", { name: "Developer mode: On" })).toHaveAttribute("aria-pressed", "true")
  })

  it("labels deterministic fallback responses without requiring developer mode", () => {
    const response: RecommendationResponse = {
      ...sharedPresentation,
      status: "matched",
      matched_filters: { category_id: "housing" },
      relaxed_level: 0,
      primary_result: evidence,
      backup_results: [],
      emergency_resources: [],
      safety_notice: null,
      limitation_notice: "This is navigation support.",
      message: "",
      error_code: "",
      intake_summary: [],
    }

    render(<RecommendationResults result={response} onStartOver={vi.fn()} />)

    expect(
      screen.getByRole("status", { name: "Response generation: Deterministic fallback" }),
    ).toBeVisible()
  })

  it("renders emergency resources before ordinary recommendations", () => {
    const response: RecommendationResponse = {
      ...sharedPresentation,
      status: "emergency",
      matched_filters: {},
      relaxed_level: 0,
      primary_result: null,
      backup_results: [],
      emergency_resources: [{
        label: "Emergency services",
        action: "Call now if there is immediate danger.",
        phone: "911",
        source_url: "https://www.quebec.ca/en/health/health-system-and-services/emergency",
      }],
      safety_notice: "Use emergency support first.",
      limitation_notice: "The navigator cannot assess emergencies.",
      message: "",
      error_code: "",
      intake_summary: [],
    }

    render(<RecommendationResults result={response} onStartOver={vi.fn()} />)
    expect(screen.getByRole("heading", { name: "Use emergency support first" })).toBeVisible()
    expect(screen.getByText("911")).toBeVisible()
    expect(screen.queryByText("Your recommended starting points")).not.toBeInTheDocument()
  })

  it("renders safe system-unavailable wording", () => {
    const response: RecommendationResponse = {
      ...sharedPresentation,
      status: "system_error",
      matched_filters: {},
      relaxed_level: 0,
      primary_result: null,
      backup_results: [],
      emergency_resources: [],
      safety_notice: null,
      limitation_notice: "Try again after the system is ready.",
      message: "Source-grounded recommendations are temporarily unavailable.",
      error_code: "retrieval_runtime_unavailable",
      intake_summary: [],
    }

    render(<RecommendationResults result={response} onStartOver={vi.fn()} />)
    expect(screen.getByRole("heading", { name: "The navigator is temporarily unavailable" })).toBeVisible()
    expect(screen.queryByText("retrieval_runtime_unavailable")).not.toBeInTheDocument()
  })
})
