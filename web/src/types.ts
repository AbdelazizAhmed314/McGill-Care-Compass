export type OptionItem = {
  id: string
  label: string
}

export type IntakeOptions = {
  categories: OptionItem[]
  need_types: OptionItem[]
  student_types: OptionItem[]
  jurisdictions: OptionItem[]
  urgency_levels: OptionItem[]
  languages: OptionItem[]
  campus_locations: OptionItem[]
  delivery_preferences: OptionItem[]
}

export type RecommendationRequest = {
  category_id: string
  need_type: string
  student_type: string
  jurisdiction: string
  language: string
  urgency_level: string
  campus_location: string
  delivery_preference: string
}

export type Evidence = {
  title: string
  excerpt: string
  canonical_url: string
  source_publisher: string
  retrieved_at: string
  source_updated_at: string
  review_status: string
  label_confidence: string
  distance: number
  match_reason: string
  limitation: string
  quality_warnings: string[]
}

export type EmergencyResource = {
  label: string
  action: string
  phone: string
  source_url: string
}

export type RecommendationStatus =
  | "matched"
  | "emergency"
  | "unsupported"
  | "no_match"
  | "low_confidence"
  | "system_error"

export type RecommendationResponse = {
  status: RecommendationStatus
  matched_filters: Record<string, unknown>
  relaxed_level: number
  primary_result: Evidence | null
  backup_results: Evidence[]
  emergency_resources: EmergencyResource[]
  safety_notice: string | null
  limitation_notice: string | null
  message: string
  error_code: string
}

export type HealthResponse = {
  status: "ok" | "warn" | "fail"
  checks: Array<{ name: string; status: string; message: string }>
}

export type MaintenanceReport = {
  generated_at: string
  counts: { pages: number; links: number; chunks: number }
  source_freshness: {
    pages_missing_source_updated_at: number
    chunks_missing_source_updated_at: number
    chunks_low_freshness_score: number
  }
  broken_links: {
    non_200_pages: number
    fetch_failed_pages: number
    not_crawled_links: number
  }
  category_coverage: {
    observed_categories: string[]
    missing_categories: string[]
    low_chunk_coverage_categories: string[]
    chunk_counts_by_category: Record<string, number>
  }
}
