import { useState, type FormEvent } from "react"

import type { IntakeOptions, OptionItem, RecommendationRequest } from "../types"

type Props = {
  options: IntakeOptions
  busy: boolean
  onSubmit: (request: RecommendationRequest) => Promise<void>
}

const initialRequest: RecommendationRequest = {
  category_id: "",
  need_type: "general_navigation",
  student_type: "",
  jurisdiction: "",
  language: "en",
  urgency_level: "routine",
  campus_location: "",
  delivery_preference: "",
  query: "",
}

export function NavigatorForm({ options, busy, onSubmit }: Props) {
  const [values, setValues] = useState(initialRequest)
  const [reviewing, setReviewing] = useState(false)

  const update = (field: keyof RecommendationRequest, value: string) => {
    setValues((current) => ({ ...current, [field]: value }))
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!reviewing) {
      setReviewing(true)
      return
    }
    await onSubmit(values)
  }

  if (reviewing) {
    return (
      <form className="intake-card review-card" onSubmit={submit}>
        <div className="section-heading">
          <span className="eyebrow">Review your intake</span>
          <h1>Check your choices</h1>
          <p>
            Your optional question is used for this match, may be processed by the
            configured response model with approved source evidence, and is not
            returned in the results.
          </p>
        </div>
        <dl className="review-grid">
          <ReviewItem label="Main need" value={labelFor(options.categories, values.category_id)} />
          <ReviewItem label="Information needed" value={labelFor(options.need_types, values.need_type)} />
          <ReviewItem label="Urgency" value={labelFor(options.urgency_levels, values.urgency_level)} />
          <ReviewItem label="Student context" value={labelFor(options.student_types, values.student_type)} />
          <ReviewItem label="System" value={labelFor(options.jurisdictions, values.jurisdiction)} />
          <ReviewItem label="Location" value={labelFor(options.campus_locations, values.campus_location)} />
          <ReviewItem label="Starting preference" value={labelFor(options.delivery_preferences, values.delivery_preference)} />
          <ReviewItem label="Source language" value={labelFor(options.languages, values.language)} />
          <ReviewItem label="Optional short question" value={values.query || "Not provided"} />
        </dl>
        <div className="form-actions review-actions">
          <button className="secondary-button" type="button" onClick={() => setReviewing(false)}>
            Edit choices
          </button>
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Checking official sources..." : "Find official starting points"}
          </button>
        </div>
      </form>
    )
  }

  return (
    <form className="intake-card" onSubmit={submit}>
      <div className="section-heading">
        <span className="eyebrow">Structured intake</span>
        <h1>Find an official starting point</h1>
        <p>
          Choose the context that fits best. Do not enter an ID, passport number,
          medical record, financial number, or other sensitive information.
        </p>
      </div>

      <fieldset>
        <legend>What do you need?</legend>
        <div className="form-grid">
          <SelectField id="category_id" label="Main need" value={values.category_id} options={options.categories} placeholder="Choose a service area" required onChange={(value) => update("category_id", value)} />
          <SelectField id="need_type" label="Information you need" value={values.need_type} options={options.need_types} onChange={(value) => update("need_type", value)} />
          <SelectField id="urgency_level" label="Urgency" value={values.urgency_level} options={options.urgency_levels} onChange={(value) => update("urgency_level", value)} />
        </div>
      </fieldset>

      <fieldset>
        <legend>Helpful context</legend>
        <p className="fieldset-note">Optional choices can make the match more specific.</p>
        <div className="form-grid">
          <SelectField id="student_type" label="Student context" value={values.student_type} options={options.student_types} placeholder="No preference" onChange={(value) => update("student_type", value)} />
          <SelectField id="jurisdiction" label="System" value={values.jurisdiction} options={options.jurisdictions} placeholder="Not sure" onChange={(value) => update("jurisdiction", value)} />
          <SelectField id="campus_location" label="Location" value={values.campus_location} options={options.campus_locations} onChange={(value) => update("campus_location", value)} />
          <SelectField id="delivery_preference" label="How you prefer to start" value={values.delivery_preference} options={options.delivery_preferences} onChange={(value) => update("delivery_preference", value)} />
          <SelectField id="language" label="Source language" value={values.language} options={options.languages} onChange={(value) => update("language", value)} />
          <label className="field full-width" htmlFor="query">
            <span>Optional short question</span>
            <textarea
              id="query"
              value={values.query}
              maxLength={300}
              rows={3}
              placeholder="For example: Where can I learn about tenant rights near campus?"
              onChange={(event) => update("query", event.target.value)}
            />
            <small className="privacy-note">
              Keep this general. Do not include names, IDs, account numbers, medical
              details, or other private information. It may be processed by the configured
              response model with approved source evidence and is not logged by this app.
              Maximum 300 characters.
            </small>
          </label>
        </div>
      </fieldset>

      <div className="form-actions">
        <p>Results provide navigation, not medical, legal, immigration, tax, or insurance decisions.</p>
        <button className="primary-button" type="submit" disabled={busy || !values.category_id}>
          Review choices
        </button>
      </div>
    </form>
  )
}

function labelFor(options: OptionItem[], id: string) {
  if (!id) return "No preference"
  return options.find((option) => option.id === id)?.label ?? id
}

function ReviewItem({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value}</dd></div>
}

type SelectProps = {
  id: string
  label: string
  value: string
  options: OptionItem[]
  placeholder?: string
  required?: boolean
  onChange: (value: string) => void
}

function SelectField({ id, label, value, options, placeholder, required, onChange }: SelectProps) {
  return (
    <label className="field" htmlFor={id}>
      <span>{label}</span>
      <select id={id} value={value} required={required} onChange={(event) => onChange(event.target.value)}>
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {options.map((option) => <option key={option.id || "blank"} value={option.id}>{option.label}</option>)}
      </select>
    </label>
  )
}
