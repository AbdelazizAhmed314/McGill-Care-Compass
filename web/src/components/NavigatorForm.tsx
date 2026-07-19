import { useState, type FormEvent } from "react"

import type { IntakeOptions, RecommendationRequest } from "../types"

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
}

export function NavigatorForm({ options, busy, onSubmit }: Props) {
  const [values, setValues] = useState(initialRequest)

  const update = (field: keyof RecommendationRequest, value: string) => {
    setValues((current) => ({ ...current, [field]: value }))
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    await onSubmit(values)
  }

  return (
    <form className="intake-card" onSubmit={submit}>
      <div className="section-heading">
        <span className="eyebrow">Structured intake</span>
        <h1>Find an official starting point</h1>
        <p>
          Choose the context that fits best. You will not be asked for an ID,
          passport number, or detailed personal information.
        </p>
      </div>

      <fieldset>
        <legend>What do you need?</legend>
        <div className="form-grid">
          <SelectField
            id="category_id"
            label="Main need"
            value={values.category_id}
            options={options.categories}
            placeholder="Choose a service area"
            required
            onChange={(value) => update("category_id", value)}
          />
          <SelectField
            id="need_type"
            label="Information you need"
            value={values.need_type}
            options={options.need_types}
            onChange={(value) => update("need_type", value)}
          />
          <SelectField
            id="urgency_level"
            label="Urgency"
            value={values.urgency_level}
            options={options.urgency_levels}
            onChange={(value) => update("urgency_level", value)}
          />
        </div>
      </fieldset>

      <fieldset>
        <legend>Helpful context</legend>
        <p className="fieldset-note">Optional choices can make the match more specific.</p>
        <div className="form-grid">
          <SelectField
            id="student_type"
            label="Student context"
            value={values.student_type}
            options={options.student_types}
            placeholder="No preference"
            onChange={(value) => update("student_type", value)}
          />
          <SelectField
            id="jurisdiction"
            label="System"
            value={values.jurisdiction}
            options={options.jurisdictions}
            placeholder="Not sure"
            onChange={(value) => update("jurisdiction", value)}
          />
          <SelectField
            id="campus_location"
            label="Location"
            value={values.campus_location}
            options={options.campus_locations}
            onChange={(value) => update("campus_location", value)}
          />
          <SelectField
            id="delivery_preference"
            label="How you prefer to start"
            value={values.delivery_preference}
            options={options.delivery_preferences}
            onChange={(value) => update("delivery_preference", value)}
          />
          <SelectField
            id="language"
            label="Source language"
            value={values.language}
            options={options.languages}
            onChange={(value) => update("language", value)}
          />
        </div>
      </fieldset>

      <div className="form-actions">
        <p>
          Results provide navigation, not medical, legal, immigration, tax, or
          insurance decisions.
        </p>
        <button className="primary-button" type="submit" disabled={busy || !values.category_id}>
          {busy ? "Checking official sources..." : "Show starting points"}
        </button>
      </div>
    </form>
  )
}

type SelectProps = {
  id: string
  label: string
  value: string
  options: Array<{ id: string; label: string }>
  placeholder?: string
  required?: boolean
  onChange: (value: string) => void
}

function SelectField({
  id,
  label,
  value,
  options,
  placeholder,
  required,
  onChange,
}: SelectProps) {
  return (
    <label className="field" htmlFor={id}>
      <span>{label}</span>
      <select
        id={id}
        value={value}
        required={required}
        onChange={(event) => onChange(event.target.value)}
      >
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.id || "blank"} value={option.id}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}
