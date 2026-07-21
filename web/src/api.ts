import type {
  HealthResponse,
  IntakeOptions,
  MaintenanceReport,
  RecommendationRequest,
  RecommendationResponse,
} from "./types"

const API_BASE = import.meta.env.VITE_API_BASE ?? ""

type ValidationDetail = { msg?: string }

async function request<T>(
  path: string,
  init?: RequestInit,
  acceptNonOk = false,
): Promise<T> {
  const response = await fetch(`${API_BASE}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  })

  if (!response.ok && !acceptNonOk) {
    let message = `Request failed with status ${response.status}`
    if (response.status === 422) {
      const body = (await response.json().catch(() => null)) as { detail?: ValidationDetail[] } | null
      message = body?.detail?.[0]?.msg?.replace(/^Value error, /, "") ?? message
    }
    throw new Error(message)
  }
  return (await response.json()) as T
}

export const api = {
  intakeOptions: () => request<IntakeOptions>("/intake/options"),
  recommendations: (payload: RecommendationRequest) =>
    request<RecommendationResponse>("/recommendations", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  health: () => request<HealthResponse>("/health/ready", undefined, true),
  maintenance: () => request<MaintenanceReport>("/maintenance/report"),
}
