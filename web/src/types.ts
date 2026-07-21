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
  query: string
}

export type IntakeSummaryItem = { label: string; value: string }

export type SourceDetails = {
  heading_path: string
  publisher: string
  source_group: string
  authority_level: string
  terms_url: string
  licence_or_terms: string
  retrieved_at: string
  source_updated_at: string
}

export type DeveloperEvidence = {
  chunk_id: string
  vector_id: string
  heading_path: string
  review_status: string
  label_method: string
  label_confidence: string
  distance: number
  quality_warnings: string[]
}

export type Evidence = {
  title: string
  category_id: string
  category_label: string
  excerpt: string
  recommended_next_step: string
  canonical_url: string
  source_publisher: string
  retrieved_at: string
  source_updated_at: string
  last_checked: string
  review_status: string
  label_confidence: string
  distance: number
  match_reason: string
  limitation: string
  quality_warnings: string[]
  source_ids_used: string[]
  supporting_evidence: DeveloperEvidence[]
  source_details: SourceDetails
  developer_details: DeveloperEvidence
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
  intake_summary: IntakeSummaryItem[]
  opening_summary: string
  limitations: string[]
  conflict_disclosure: {
    has_conflict: boolean
    what_differs: string
    why_this_route_was_chosen: string
    how_to_double_check: string
    source_ids_considered: string[]
  }
  official_sources: Array<{ label: string; url: string; source_id: string }>
  generation_mode: "llm" | "deterministic"
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
