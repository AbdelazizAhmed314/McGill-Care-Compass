import { useEffect, useState } from "react"

import { api } from "../api"
import type { HealthResponse, MaintenanceReport } from "../types"

export function StatusPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [report, setReport] = useState<MaintenanceReport | null>(null)
  const [healthFailed, setHealthFailed] = useState(false)
  const [reportFailed, setReportFailed] = useState(false)

  useEffect(() => {
    let active = true
    api.health()
      .then((value) => {
        if (active) setHealth(value)
      })
      .catch(() => {
        if (active) setHealthFailed(true)
      })
    api.maintenance()
      .then((value) => {
        if (active) setReport(value)
      })
      .catch(() => {
        if (active) setReportFailed(true)
      })
    return () => {
      active = false
    }
  }, [])

  const observedCategoryCount = report
    ? Object.keys(report.category_coverage.by_category ?? {}).length ||
      report.category_coverage.observed_categories?.length ||
      0
    : 0
  const attentionCategoryCount = report
    ? new Set([
        ...(report.category_coverage.categories_without_pages ?? []),
        ...(report.category_coverage.categories_without_chunks ?? []),
        ...(report.category_coverage.low_chunk_coverage_categories ?? []),
      ]).size
    : 0
  const failedSourceCount = report
    ? report.failed_sources?.count ??
      report.source_freshness.fetch_failed_count ??
      report.broken_links?.non_200_pages ??
      0
    : 0
  const missingSourceDateCount = report
    ? report.source_freshness.source_updated_at_missing_count ??
      report.source_freshness.chunks_missing_source_updated_at ??
      0
    : 0

  return (
    <main className="page-shell status-page">
      <div className="section-heading">
        <span className="eyebrow">System transparency</span>
        <h1>Navigator status</h1>
        <p>Runtime readiness and source-maintenance signals for the internal team.</p>
      </div>

      {(healthFailed || reportFailed) && (
        <div className="status-notice warn">
          Some operational details are unavailable. Student-facing safety fallbacks remain active.
        </div>
      )}

      <section className="status-card">
        <div>
          <span className="card-kicker">Application readiness</span>
          <h2 className={`status-value ${health?.status ?? "loading"}`}>
            {health?.status ?? (healthFailed ? "Unavailable" : "Checking")}
          </h2>
        </div>
        <div className="checks-list">
          {health?.checks.map((check) => (
            <div className="check-row" key={check.name}>
              <span className={`check-dot ${check.status}`} aria-hidden="true" />
              <div>
                <strong>{check.name.replaceAll("_", " ")}</strong>
                <p>{check.message}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {report && (
        <>
          <div className="metrics-grid">
            <Metric label="Source pages" value={report.counts.pages} />
            <Metric label="Source links" value={report.counts.links} />
            <Metric label="Evidence chunks" value={report.counts.chunks} />
            <Metric label="Observed categories" value={observedCategoryCount} />
          </div>
          <section className="status-card maintenance-card">
            <div>
              <span className="card-kicker">Maintenance attention</span>
              <h2>Signals requiring review</h2>
              <p>Generated {new Date(report.generated_at ?? report.as_of ?? "").toLocaleString("en-CA")}</p>
            </div>
            <ul className="attention-list">
              <li>
                <strong>{failedSourceCount}</strong>
                failed source fetches
              </li>
              <li>
                <strong>{missingSourceDateCount}</strong>
                sources without an updated date
              </li>
              <li>
                <strong>{attentionCategoryCount}</strong>
                categories requiring coverage review
              </li>
            </ul>
          </section>
        </>
      )}
    </main>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <article className="metric-card">
      <strong>{value.toLocaleString("en-CA")}</strong>
      <span>{label}</span>
    </article>
  )
}