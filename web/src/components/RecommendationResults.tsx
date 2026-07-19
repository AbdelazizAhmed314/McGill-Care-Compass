import type { Evidence, RecommendationResponse } from "../types"

type Props = {
  result: RecommendationResponse
  onStartOver: () => void
}

const statusTitles = {
  unsupported: "This need is outside the current navigator",
  no_match: "No source-grounded match was found",
  low_confidence: "The available evidence was not strong enough",
  system_error: "The navigator is temporarily unavailable",
}

export function RecommendationResults({ result, onStartOver }: Props) {
  if (result.status === "emergency") {
    return (
      <section className="result-shell emergency-panel" aria-live="assertive">
        <span className="eyebrow">Immediate safety guidance</span>
        <h1>Use emergency support first</h1>
        <p className="lead">{result.safety_notice}</p>
        <div className="resource-grid">
          {result.emergency_resources.map((resource) => (
            <article className="resource-card" key={resource.label}>
              <h2>{resource.label}</h2>
              <p>{resource.action}</p>
              {resource.phone && <strong>{resource.phone}</strong>}
              {resource.source_url && (
                <a href={resource.source_url} target="_blank" rel="noreferrer">
                  Open official resource
                </a>
              )}
            </article>
          ))}
        </div>
        <p className="limitation">{result.limitation_notice}</p>
        <button className="secondary-button" type="button" onClick={onStartOver}>
          Start over
        </button>
      </section>
    )
  }

  if (result.status !== "matched" || !result.primary_result) {
    const title = statusTitles[result.status as keyof typeof statusTitles] ?? "No result available"
    return (
      <section className="result-shell fallback-panel" aria-live="polite">
        <span className="eyebrow">Navigator response</span>
        <h1>{title}</h1>
        <p className="lead">{result.message}</p>
        {result.limitation_notice && <p className="limitation">{result.limitation_notice}</p>}
        <button className="primary-button" type="button" onClick={onStartOver}>
          Adjust your choices
        </button>
      </section>
    )
  }

  return (
    <section className="result-shell" aria-live="polite">
      <div className="results-header">
        <div>
          <span className="eyebrow">Source-grounded result</span>
          <h1>Your primary starting point</h1>
        </div>
        <button className="text-button" type="button" onClick={onStartOver}>
          Start over
        </button>
      </div>

      <EvidenceCard evidence={result.primary_result} primary />

      {result.backup_results.length > 0 && (
        <div className="backup-section">
          <h2>Backup options</h2>
          <div className="backup-grid">
            {result.backup_results.map((evidence) => (
              <EvidenceCard key={evidence.canonical_url + evidence.title} evidence={evidence} />
            ))}
          </div>
        </div>
      )}

      {result.limitation_notice && (
        <aside className="limitation" aria-label="Important limitation">
          <strong>Important limitation</strong>
          <p>{result.limitation_notice}</p>
        </aside>
      )}
    </section>
  )
}

function EvidenceCard({ evidence, primary = false }: { evidence: Evidence; primary?: boolean }) {
  return (
    <article className={primary ? "evidence-card primary-evidence" : "evidence-card"}>
      <div className="evidence-label">{primary ? "Best available match" : "Alternative"}</div>
      <h2>{evidence.title}</h2>
      <p className="match-reason">{evidence.match_reason}</p>
      <p className="evidence-excerpt">{evidence.excerpt}</p>
      <dl className="source-meta">
        <div>
          <dt>Publisher</dt>
          <dd>{evidence.source_publisher || "Official source"}</dd>
        </div>
        <div>
          <dt>Retrieved</dt>
          <dd>{formatDate(evidence.retrieved_at)}</dd>
        </div>
        <div>
          <dt>Source updated</dt>
          <dd>{evidence.source_updated_at ? formatDate(evidence.source_updated_at) : "Not listed"}</dd>
        </div>
      </dl>
      <a className="source-link" href={evidence.canonical_url} target="_blank" rel="noreferrer">
        Continue to official source <span aria-hidden="true">-&gt;</span>
      </a>
    </article>
  )
}

function formatDate(value: string) {
  if (!value) return "Not listed"
  const date = new Date(value)
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat("en-CA", { dateStyle: "medium" }).format(date)
}
