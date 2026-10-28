import { useState } from 'react'
import { api, CM_PER_IN, LB_PER_KG } from '../api'
import Targets from './Targets'

const ACTIVITY = [
  ['sedentary', 'Sedentary (desk job, little exercise)'],
  ['light', 'Light (1-3 workouts/week)'],
  ['moderate', 'Moderate (3-5 workouts/week)'],
  ['active', 'Active (6-7 workouts/week)'],
  ['very_active', 'Very active (physical job + training)'],
]

function toForm(profile, units) {
  if (!profile) {
    return { sex: 'male', age: '', feet: '', inches: '', height: '', weight: '', activity: 'moderate', goal: 'cut', pace: 'moderate' }
  }
  const totalIn = profile.height_cm / CM_PER_IN
  return {
    ...profile,
    feet: Math.floor(totalIn / 12),
    inches: Math.round(totalIn % 12),
    height: Math.round(profile.height_cm),
    weight: Math.round((units === 'imperial' ? profile.weight_kg * LB_PER_KG : profile.weight_kg) * 10) / 10,
  }
}

function toProfile(form, units) {
  const height_cm = units === 'imperial'
    ? (Number(form.feet) * 12 + Number(form.inches || 0)) * CM_PER_IN
    : Number(form.height)
  const weight_kg = units === 'imperial' ? Number(form.weight) / LB_PER_KG : Number(form.weight)
  return {
    sex: form.sex,
    age: Number(form.age),
    height_cm: Math.round(height_cm * 10) / 10,
    weight_kg: Math.round(weight_kg * 10) / 10,
    activity: form.activity,
    goal: form.goal,
    pace: form.pace,
  }
}

export default function ProfileForm({ profile, units, setUnits, onSaved }) {
  const [form, setForm] = useState(() => toForm(profile, units))
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const set = (key) => (e) => {
    setForm({ ...form, [key]: e.target.value })
    setPreview(null)
  }

  const switchUnits = (next) => {
    if (next === units) return
    const metricProfile = toProfile(form, units)
    setUnits(next)
    if (form.weight !== '') setForm({ ...form, ...toForm({ ...form, ...metricProfile }, next) })
  }

  async function run(action) {
    setError('')
    setBusy(true)
    try {
      const body = toProfile(form, units)
      if (action === 'preview') setPreview(await api.calculate(body))
      else onSaved(await api.saveProfile(body))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>{profile ? 'Edit profile' : "Let's estimate your targets"}</h2>
      <form className="profile-form" onSubmit={(e) => { e.preventDefault(); run('preview') }}>
        <fieldset className="toggle">
          <legend>Units</legend>
          {['imperial', 'metric'].map((u) => (
            <button type="button" key={u} aria-pressed={units === u} onClick={() => switchUnits(u)}>
              {u === 'imperial' ? 'lb / ft' : 'kg / cm'}
            </button>
          ))}
        </fieldset>

        <label>Sex
          <select value={form.sex} onChange={set('sex')}>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </label>
        <label>Age
          <input type="number" min="13" max="100" required value={form.age} onChange={set('age')} />
        </label>

        {units === 'imperial' ? (
          <div className="row">
            <label>Height (ft)
              <input type="number" min="3" max="8" required value={form.feet} onChange={set('feet')} />
            </label>
            <label>(in)
              <input type="number" min="0" max="11" value={form.inches} onChange={set('inches')} />
            </label>
          </div>
        ) : (
          <label>Height (cm)
            <input type="number" min="100" max="250" required value={form.height} onChange={set('height')} />
          </label>
        )}
        <label>Weight ({units === 'imperial' ? 'lb' : 'kg'})
          <input type="number" step="0.1" min="1" required value={form.weight} onChange={set('weight')} />
        </label>

        <label>Activity
          <select value={form.activity} onChange={set('activity')}>
            {ACTIVITY.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </label>

        <fieldset className="toggle">
          <legend>Goal</legend>
          {[['cut', 'Lose fat'], ['maintain', 'Maintain'], ['bulk', 'Build muscle']].map(([v, l]) => (
            <button type="button" key={v} aria-pressed={form.goal === v} onClick={() => set('goal')({ target: { value: v } })}>
              {l}
            </button>
          ))}
        </fieldset>
        {form.goal !== 'maintain' && (
          <label>Pace
            <select value={form.pace} onChange={set('pace')}>
              <option value="slow">Slow</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </label>
        )}

        {error && <p className="error" role="alert">{error}</p>}
        <div className="actions">
          <button type="submit" disabled={busy}>Calculate</button>
          {preview && (
            <button type="button" className="primary" disabled={busy} onClick={() => run('save')}>
              Save &amp; start tracking
            </button>
          )}
        </div>
      </form>
      {preview && <Targets targets={preview} units={units} />}
    </div>
  )
}
