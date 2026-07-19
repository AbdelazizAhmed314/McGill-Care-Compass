import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import type { IntakeOptions, RecommendationResponse } from "../types"
import { NavigatorForm } from "./NavigatorForm"
import { RecommendationResults } from "./RecommendationResults"

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

describe("navigator safety contract", () => {
  it("submits structured choices without a free-text field", async () => {
    const submit = vi.fn().mockResolvedValue(undefined)
    render(<NavigatorForm options={options} busy={false} onSubmit={submit} />)

    expect(screen.queryByRole("textbox")).not.toBeInTheDocument()
    await userEvent.selectOptions(screen.getByLabelText("Main need"), "housing")
    await userEvent.click(screen.getByRole("button", { name: "Show starting points" }))

    expect(submit).toHaveBeenCalledWith(
      expect.objectContaining({ category_id: "housing", urgency_level: "routine" }),
    )
  })

  it("renders emergency resources before ordinary recommendations", () => {
    const response: RecommendationResponse = {
      status: "emergency",
      matched_filters: {},
      relaxed_level: 0,
      primary_result: null,
      backup_results: [],
      emergency_resources: [
        {
          label: "Emergency services",
          action: "Call now if there is immediate danger.",
          phone: "911",
          source_url: "https://www.quebec.ca/en/health/health-system-and-services/emergency",
        },
      ],
      safety_notice: "Use emergency support first.",
      limitation_notice: "The navigator cannot assess emergencies.",
      message: "",
      error_code: "",
    }

    render(<RecommendationResults result={response} onStartOver={vi.fn()} />)

    expect(screen.getByRole("heading", { name: "Use emergency support first" })).toBeVisible()
    expect(screen.getByText("911")).toBeVisible()
    expect(screen.queryByText("Your primary starting point")).not.toBeInTheDocument()
  })

  it("renders safe system-unavailable wording", () => {
    const response: RecommendationResponse = {
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
    }

    render(<RecommendationResults result={response} onStartOver={vi.fn()} />)

    expect(screen.getByRole("heading", { name: "The navigator is temporarily unavailable" })).toBeVisible()
    expect(screen.queryByText("retrieval_runtime_unavailable")).not.toBeInTheDocument()
  })
})
