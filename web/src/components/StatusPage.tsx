import { useEffect, useState } from "react"

import { api } from "../api"
import type { HealthResponse, MaintenanceReport } from "../types"

export function StatusPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [report, setReport] = useState<MaintenanceReport | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let active = true
    Promise.allSettled([api.health(), api.maintenance()]).then(([healthResult, reportResult]) => {
      if (!active) return
      if (healthResult.status === "fulfilled") setHealth(healthResult.value)
      if (reportResult.status === "fulfilled") setReport(reportResult.value)
      setFailed(healthResult.status === "rejected" || reportResult.status === "rejected")
    })
    return () => {
      active = false
    }
  }, [])

  return (
    <main className="page-shell status-page">
      <div className="section-heading">
        <span className="eyebrow">System transparency</span>
        <h1>Navigator status</h1>
        <p>Runtime readiness and source-maintenance signals for the internal team.</p>
      </div>

      {failed && (
        <div className="status-notice warn">
          Some operational details are unavailable. Student-facing safety fallbacks remain active.
        </div>
      )}

      <section className="status-card">
        <div>
          <span className="card-kicker">Application readiness</span>
          <h2 className={`status-value ${health?.status ?? "loading"}`}>
            {health?.status ?? "Checking"}
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
            <Metric
              label="Observed categories"
              value={report.category_coverage.observed_categories.length}
            />
          </div>
          <section className="status-card maintenance-card">
            <div>
              <span className="card-kicker">Maintenance attention</span>
              <h2>Signals requiring review</h2>
              <p>Generated {new Date(report.generated_at).toLocaleString("en-CA")}</p>
            </div>
            <ul className="attention-list">
              <li>
                <strong>{report.broken_links.non_200_pages}</strong>
                non-200 source pages
              </li>
              <li>
                <strong>{report.source_freshness.chunks_missing_source_updated_at}</strong>
                chunks without a source-updated date
              </li>
              <li>
                <strong>{report.category_coverage.low_chunk_coverage_categories.length}</strong>
                low-coverage categories
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
