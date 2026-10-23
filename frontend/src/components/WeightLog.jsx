import { useState } from 'react'
import { api, toKg, today } from '../api'

export default function WeightLog({ units, onLogged }) {
  const [date, setDate] = useState(today())
  const [weight, setWeight] = useState('')
  const [error, setError] = useState('')
  const unit = units === 'imperial' ? 'lb' : 'kg'

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      const saved = await api.addWeight({ date, weight_kg: Math.round(toKg(Number(weight), units) * 100) / 100 })
      setWeight('')
      onLogged(saved)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <section className="card" aria-labelledby="weight-heading">
      <h2 id="weight-heading">Weigh-in</h2>
      <form className="weight-form" onSubmit={handleSubmit}>
        <input type="date" value={date} max={today()} onChange={(e) => setDate(e.target.value)} aria-label="Weigh-in date" />
        <input
          type="number" step="0.1" min="1" required placeholder={`Weight (${unit})`} value={weight}
          onChange={(e) => setWeight(e.target.value)} aria-label={`Weight in ${unit}`}
        />
        <button type="submit">Log weight</button>
      </form>
      {error && <p className="error" role="alert">{error}</p>}
      <p className="muted small">Your latest weigh-in updates your targets automatically. Logging the same date again overwrites it.</p>
    </section>
  )
}
