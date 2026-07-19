import { useEffect, useState } from "react"

import { api } from "./api"
import { NavigatorForm } from "./components/NavigatorForm"
import { RecommendationResults } from "./components/RecommendationResults"
import { StatusPage } from "./components/StatusPage"
import type { IntakeOptions, RecommendationRequest, RecommendationResponse } from "./types"

type View = "home" | "navigator" | "status"

function viewFromPath(): View {
  if (window.location.pathname.startsWith("/status")) return "status"
  if (window.location.pathname.startsWith("/navigator")) return "navigator"
  return "home"
}

export function App() {
  const [view, setView] = useState<View>(viewFromPath)

  useEffect(() => {
    const update = () => setView(viewFromPath())
    window.addEventListener("popstate", update)
    return () => window.removeEventListener("popstate", update)
  }, [])

  const navigate = (next: View) => {
    const path = next === "home" ? "/" : `/${next}`
    window.history.pushState({}, "", path)
    setView(next)
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  return (
    <div className="app">
      <Header view={view} navigate={navigate} />
      {view === "home" && <Home onStart={() => navigate("navigator")} />}
      {view === "navigator" && <NavigatorPage />}
      {view === "status" && <StatusPage />}
      <Footer />
    </div>
  )
}

function Header({ view, navigate }: { view: View; navigate: (view: View) => void }) {
  return (
    <header className="site-header">
      <button className="brand" type="button" onClick={() => navigate("home")}>
        <span className="brand-mark" aria-hidden="true">C</span>
        <span>
          <strong>Care Compass</strong>
          <small>McGill newcomer navigator</small>
        </span>
      </button>
      <nav aria-label="Primary navigation">
        <button
          className={view === "navigator" ? "active" : ""}
          type="button"
          onClick={() => navigate("navigator")}
        >
          Navigator
        </button>
        <button
          className={view === "status" ? "active" : ""}
          type="button"
          onClick={() => navigate("status")}
        >
          Status
        </button>
      </nav>
    </header>
  )
}

function Home({ onStart }: { onStart: () => void }) {
  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">For newcomer students at McGill</span>
          <h1>Find the right official door to knock on.</h1>
          <p className="hero-lead">
            A short, private intake connects your situation to a small set of
            source-grounded starting points across McGill, Quebec, and Canada.
          </p>
          <div className="hero-actions">
            <button className="primary-button" type="button" onClick={onStart}>
              Find a starting point
            </button>
            <span>No account. No sensitive identifiers.</span>
          </div>
        </div>
        <div className="compass-visual" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="compass-core">
            <span>N</span>
            <strong>CC</strong>
            <span>S</span>
          </div>
          <div className="signal signal-one">McGill</div>
          <div className="signal signal-two">Quebec</div>
          <div className="signal signal-three">Canada</div>
        </div>
      </section>

      <section className="trust-strip" aria-label="Navigator principles">
        <article>
          <span>01</span>
          <div>
            <h2>Official sources first</h2>
            <p>Recommendations link back to governed source evidence.</p>
          </div>
        </article>
        <article>
          <span>02</span>
          <div>
            <h2>Clear boundaries</h2>
            <p>Navigation support, never diagnosis or eligibility decisions.</p>
          </div>
        </article>
        <article>
          <span>03</span>
          <div>
            <h2>Minimal information</h2>
            <p>Structured choices without collecting sensitive identifiers.</p>
          </div>
        </article>
      </section>

      <section className="how-it-works">
        <div className="section-heading">
          <span className="eyebrow">A careful first step</span>
          <h2>From uncertainty to an official next action</h2>
        </div>
        <div className="step-grid">
          <article>
            <span className="step-number">1</span>
            <h3>Choose your need</h3>
            <p>Select the service area, information type, and urgency.</p>
          </article>
          <article>
            <span className="step-number">2</span>
            <h3>Add useful context</h3>
            <p>Optional choices refine the match without asking for private details.</p>
          </article>
          <article>
            <span className="step-number">3</span>
            <h3>Review official routes</h3>
            <p>See a primary starting point, backups, evidence, and limitations.</p>
          </article>
        </div>
      </section>
    </main>
  )
}

function NavigatorPage() {
  const [options, setOptions] = useState<IntakeOptions | null>(null)
  const [result, setResult] = useState<RecommendationResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    api.intakeOptions().then(setOptions).catch(() => {
      setError("The navigator options could not be loaded. Check the backend status.")
    })
  }, [])

  const submit = async (request: RecommendationRequest) => {
    setBusy(true)
    setError("")
    try {
      setResult(await api.recommendations(request))
    } catch {
      setError("The navigator could not complete this request. Please try again later.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="page-shell navigator-page">
      {error && <div className="status-notice error" role="alert">{error}</div>}
      {!result && options && <NavigatorForm options={options} busy={busy} onSubmit={submit} />}
      {!result && !options && !error && (
        <div className="loading-card" aria-live="polite">Loading navigator choices...</div>
      )}
      {result && <RecommendationResults result={result} onStartOver={() => setResult(null)} />}
    </main>
  )
}

function Footer() {
  return (
    <footer>
      <div>
        <strong>McGill Care Compass</strong>
        <p>Source-grounded service navigation for newcomer students.</p>
      </div>
      <p>
        Confirm current details with the linked official source. This prototype
        does not provide professional advice or emergency assessment.
      </p>
    </footer>
  )
}
