import { cleanup, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { api } from "../api"
import { StatusPage } from "./StatusPage"

vi.mock("../api", () => ({
  api: {
    health: vi.fn(),
    maintenance: vi.fn(),
  },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe("status page", () => {
  it("renders the strengthened maintenance schema without remaining on Checking", async () => {
    vi.mocked(api.health).mockResolvedValue({
      status: "ok",
      checks: [{ name: "chroma", status: "ok", message: "4,239 chunks ready." }],
    })
    vi.mocked(api.maintenance).mockResolvedValue({
      as_of: "2026-07-25T00:00:00Z",
      counts: { pages: 490, links: 1000, chunks: 4239 },
      source_freshness: {
        source_updated_at_missing_count: 44,
        fetch_failed_count: 4,
      },
      failed_sources: { count: 4 },
      category_coverage: {
        by_category: {
          academics: {},
          housing: {},
        },
        categories_without_pages: ["language_integration"],
        categories_without_chunks: [],
      },
    })

    render(<StatusPage />)

    expect(await screen.findByRole("heading", { name: "ok" })).toBeVisible()
    expect(screen.getByText("4,239")).toBeVisible()
    expect(screen.getByText("2")).toBeVisible()
    expect(screen.getByText("failed source fetches")).toBeVisible()
    expect(screen.queryByText("Checking")).not.toBeInTheDocument()
    expect(screen.queryByText("Generated Invalid Date")).not.toBeInTheDocument()
  })

  it("shows health as soon as it resolves while maintenance is pending", async () => {
    vi.mocked(api.health).mockResolvedValue({ status: "ok", checks: [] })
    vi.mocked(api.maintenance).mockImplementation(() => new Promise(() => undefined))

    render(<StatusPage />)

    await waitFor(() => expect(screen.getByRole("heading", { name: "ok" })).toBeVisible())
  })
})