import { toDisplayWeight } from '../api'
import Metric from './Metric'

const SECONDARY = ['fat', 'carbs', 'fiber', 'water', 'tdee', 'bmr', 'bmi', 'weekly_change_kg']

export default function Targets({ targets, units }) {
  const weekly = targets.weekly_change_kg.value
  const weeklyDisplay = `${weekly > 0 ? '+' : ''}${toDisplayWeight(weekly, units)} ${units === 'imperial' ? 'lb' : 'kg'}/wk`
  return (
    <section className="targets" aria-label="Daily targets">
      <div className="targets__headline">
        <Metric name="calories" metric={targets.calories} headline />
        <Metric name="protein" metric={targets.protein} headline />
      </div>
      <div className="targets__grid">
        {SECONDARY.map((key) => (
          <Metric
            key={key}
            name={key}
            metric={targets[key]}
            displayValue={key === 'weekly_change_kg' ? weeklyDisplay : undefined}
          />
        ))}
      </div>
      <p className="hint">Hover or tab to any number to see why it matters.</p>
    </section>
  )
}
