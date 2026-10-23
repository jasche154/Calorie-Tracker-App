import { api } from '../api'

const BARS = [
  ['calories', 'Calories', 'kcal'],
  ['protein', 'Protein', 'g'],
  ['carbs', 'Carbs', 'g'],
  ['fat', 'Fat', 'g'],
]

function ProgressBar({ label, value, target, unit }) {
  const pct = target ? Math.min((value / target) * 100, 100) : 0
  const isOver = target && value > target * 1.05
  return (
    <div className="bar">
      <div className="bar__label">
        <span>{label}</span>
        <span><strong>{Math.round(value)}</strong> / {Math.round(target)} {unit}</span>
      </div>
      <div className="bar__track" role="progressbar" aria-label={label} aria-valuenow={Math.round(value)} aria-valuemax={Math.round(target)}>
        <div className={`bar__fill bar__fill--${isOver ? 'over' : label.toLowerCase()}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function DailyLog({ log, targets, onChanged }) {
  async function handleDelete(id) {
    await api.deleteLog(id)
    onChanged()
  }
  const remaining = Math.round(targets.calories.value - log.totals.calories)

  return (
    <section className="card" aria-labelledby="log-heading">
      <div className="card__head">
        <h2 id="log-heading">Today's log</h2>
        <span className={`pill ${remaining < 0 ? 'pill--over' : ''}`}>
          {remaining >= 0 ? `${remaining} kcal left` : `${-remaining} kcal over`}
        </span>
      </div>
      {BARS.map(([key, label, unit]) => (
        <ProgressBar key={key} label={label} unit={unit} value={log.totals[key]} target={targets[key].value} />
      ))}
      {log.entries.length === 0 ? (
        <p className="muted">Nothing logged yet. Search for a food to get started.</p>
      ) : (
        <ul className="entries">
          {log.entries.map((e) => (
            <li key={e.id}>
              <span>{e.food.name} <span className="muted">{e.grams} g</span></span>
              <span>{Math.round(e.calories)} kcal · {e.protein} g P</span>
              <button type="button" className="ghost" aria-label={`Remove ${e.food.name}`} onClick={() => handleDelete(e.id)}>✕</button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
