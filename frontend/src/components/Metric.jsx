import { useId } from 'react'

const LABELS = {
  calories: 'Calories',
  protein: 'Protein',
  fat: 'Fat',
  carbs: 'Carbs',
  fiber: 'Fiber',
  water: 'Water',
  bmr: 'BMR',
  tdee: 'Maintenance (TDEE)',
  bmi: 'BMI',
  weekly_change_kg: 'Weekly change',
}

/** A metric card. Hover (or keyboard focus) shows why the metric matters. */
export default function Metric({ name, metric, headline = false, displayValue }) {
  const tipId = useId()
  return (
    <div
      className={`metric ${headline ? 'metric--headline' : ''}`}
      tabIndex={0}
      aria-describedby={tipId}
      data-metric={name}
    >
      <span className="metric__label">{LABELS[name] ?? name}</span>
      <span className="metric__value">
        {displayValue ?? metric.value.toLocaleString()} <small>{displayValue ? '' : metric.unit}</small>
      </span>
      <span role="tooltip" id={tipId} className="metric__tip">
        {metric.why}
      </span>
    </div>
  )
}
