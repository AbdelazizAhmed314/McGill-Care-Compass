import type {
  HealthResponse,
  IntakeOptions,
  MaintenanceReport,
  RecommendationRequest,
  RecommendationResponse,
} from "./types"

const API_BASE = import.meta.env.VITE_API_BASE ?? ""

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
    throw new Error(`Request failed with status ${response.status}`)
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
