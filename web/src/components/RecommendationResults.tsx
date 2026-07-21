import { useState } from "react"

import type { DeveloperEvidence, Evidence, RecommendationResponse } from "../types"

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
  const [developerMode, setDeveloperMode] = useState(false)

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
    const title =
      statusTitles[result.status as keyof typeof statusTitles] ?? "No result available"
    return (
      <section className="result-shell fallback-panel" aria-live="polite">
        <span className="eyebrow">Navigator response</span>
        <h1>{title}</h1>
        <p className="lead">{result.message}</p>
        {result.limitation_notice && (
          <p className="limitation">{result.limitation_notice}</p>
        )}
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
          <span className="eyebrow">Source-grounded response</span>
          <h1>Your recommended starting points</h1>
        </div>
        <div className="result-controls">
          <button
            className="developer-toggle"
            type="button"
            aria-pressed={developerMode}
            onClick={() => setDeveloperMode((enabled) => !enabled)}
          >
            Developer mode: {developerMode ? "On" : "Off"}
          </button>
          <button className="text-button" type="button" onClick={onStartOver}>
            Start over
          </button>
        </div>
      </div>

      {result.opening_summary && <p className="lead result-opening">{result.opening_summary}</p>}

      {result.intake_summary.length > 0 && (
        <section className="intake-summary" aria-label="Intake summary">
          <h2>Based on your selections</h2>
          <dl>
            {result.intake_summary.map((item) => (
              <div key={item.label}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </section>
      )}

      <EvidenceCard
        evidence={result.primary_result}
        primary
        developerMode={developerMode}
      />

      {result.backup_results.length > 0 && (
        <div className="backup-section">
          <h2>Backup options</h2>
          <div className="backup-grid">
            {result.backup_results.map((evidence) => (
              <EvidenceCard
                key={evidence.canonical_url}
                evidence={evidence}
                developerMode={developerMode}
              />
            ))}
          </div>
        </div>
      )}

      {result.conflict_disclosure.has_conflict && (
        <aside className="conflict-panel" aria-label="Important double-check">
          <strong>Important double-check</strong>
          {result.conflict_disclosure.what_differs && (
            <p><b>What differs:</b> {result.conflict_disclosure.what_differs}</p>
          )}
          {result.conflict_disclosure.why_this_route_was_chosen && (
            <p>
              <b>Why this route was chosen:</b>{" "}
              {result.conflict_disclosure.why_this_route_was_chosen}
            </p>
          )}
          {result.conflict_disclosure.how_to_double_check && (
            <p>
              <b>How to double-check:</b>{" "}
              {result.conflict_disclosure.how_to_double_check}
            </p>
          )}
        </aside>
      )}

      {result.limitations.length > 0 && (
        <aside className="limitation" aria-label="Important limitations">
          <strong>Important limitations</strong>
          <ul>
            {result.limitations.map((limitation) => (
              <li key={limitation}>{limitation}</li>
            ))}
          </ul>
        </aside>
      )}

      {result.official_sources.length > 0 && (
        <section className="official-source-list">
          <h2>Official sources used</h2>
          <ul>
            {result.official_sources.map((source) => (
              <li key={source.source_id}>
                <a href={source.url} target="_blank" rel="noreferrer">
                  {source.label || "Official source"}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      {developerMode && (
        <aside className="developer-panel" aria-label="Retrieval diagnostics">
          <h2>Retrieval diagnostics</h2>
          <dl>
            <Meta label="Generation mode" value={result.generation_mode} />
            <Meta label="Relaxation level" value={String(result.relaxed_level)} />
            <Meta
              label="Matched filters"
              value={JSON.stringify(result.matched_filters)}
            />
          </dl>
        </aside>
      )}
    </section>
  )
}

function EvidenceCard({
  evidence,
  primary = false,
  developerMode,
}: {
  evidence: Evidence
  primary?: boolean
  developerMode: boolean
}) {
  const details = evidence.source_details
  return (
    <article className={primary ? "evidence-card primary-evidence" : "evidence-card"}>
      <div className="evidence-label">
        {primary ? "Primary recommendation" : "Backup recommendation"}
      </div>
      <h2>{evidence.title}</h2>
      <p className="category-label">{evidence.category_label}</p>

      <div className="result-field">
        <h3>Why this may help</h3>
        <p>{evidence.match_reason}</p>
      </div>
      <div className="result-field">
        <h3>Recommended next step</h3>
        <p>{evidence.recommended_next_step}</p>
      </div>
      <aside className="item-limitation">
        <strong>Important limitation</strong>
        <p>{evidence.limitation}</p>
      </aside>

      <a
        className="source-link"
        href={evidence.canonical_url}
        target="_blank"
        rel="noreferrer"
      >
        Continue to official source <span aria-hidden="true">-&gt;</span>
      </a>
      <p className="last-checked">Last checked: {formatDate(evidence.last_checked)}</p>

      <details className="source-details">
        <summary>Source details</summary>
        <dl className="source-meta">
          <Meta
            label="Publisher"
            value={details.publisher || evidence.source_publisher || "Official source"}
          />
          <Meta label="Heading" value={details.heading_path || "Not listed"} />
          <Meta label="Source group" value={details.source_group || "Not listed"} />
          <Meta label="Authority level" value={details.authority_level || "Not listed"} />
          <Meta
            label="Retrieved"
            value={formatDate(details.retrieved_at || evidence.retrieved_at)}
          />
          <Meta
            label="Source updated"
            value={formatDate(details.source_updated_at || evidence.source_updated_at)}
          />
          <Meta
            label="Licence or terms"
            value={details.licence_or_terms || "Not listed"}
          />
        </dl>
        {details.terms_url && (
          <a href={details.terms_url} target="_blank" rel="noreferrer">
            View source terms
          </a>
        )}
      </details>

      <details className="source-details">
        <summary>View supporting source excerpt</summary>
        <p className="evidence-excerpt">{evidence.excerpt}</p>
      </details>

      {developerMode && (
        <aside
          className="developer-panel"
          aria-label={`Developer evidence for ${evidence.title}`}
        >
          <h3>Developer evidence</h3>
          <p>Source IDs used: {evidence.source_ids_used.join(", ")}</p>
          {evidence.supporting_evidence.map((item, index) => (
            <DeveloperChunk
              key={item.chunk_id || item.vector_id}
              item={item}
              index={index}
            />
          ))}
        </aside>
      )}
    </article>
  )
}

function DeveloperChunk({
  item,
  index,
}: {
  item: DeveloperEvidence
  index: number
}) {
  return (
    <section className="developer-chunk">
      <h4>Supporting chunk {index + 1}</h4>
      <dl>
        <Meta label="Chunk ID" value={item.chunk_id || "Not listed"} />
        <Meta label="Vector ID" value={item.vector_id || "Not listed"} />
        <Meta label="Heading path" value={item.heading_path || "Not listed"} />
        <Meta label="Review status" value={item.review_status || "Not listed"} />
        <Meta label="Label method" value={item.label_method || "Not listed"} />
        <Meta
          label="Label confidence"
          value={item.label_confidence || "Not listed"}
        />
        <Meta
          label="Distance"
          value={Number.isFinite(item.distance) ? item.distance.toFixed(4) : "Not listed"}
        />
        <Meta
          label="Quality warnings"
          value={item.quality_warnings.length ? item.quality_warnings.join(", ") : "None"}
        />
      </dl>
    </section>
  )
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  )
}

function formatDate(value: string) {
  if (!value) return "Not listed"
  const date = new Date(value)
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat("en-CA", { dateStyle: "medium" }).format(date)
}
