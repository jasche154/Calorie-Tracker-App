import { useEffect, useState } from 'react'
import {
  Bar, BarChart, CartesianGrid, ComposedChart, Line, ReferenceLine,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { api, toDisplayWeight } from '../api'

const RANGES = [7, 30, 90]
const shortDate = (iso) => iso.slice(5).replace('-', '/')

export default function Charts({ units, refreshKey }) {
  const [days, setDays] = useState(30)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let isCurrent = true
    api.getProgress(days)
      .then((d) => { if (isCurrent) { setData(d); setError('') } })
      .catch((err) => { if (isCurrent) setError(err.message) })
    return () => { isCurrent = false }
  }, [days, refreshKey])

  if (error) return <p className="error" role="alert">{error}</p>
  if (!data) return <p className="muted">Loading progress…</p>

  const unit = units === 'imperial' ? 'lb' : 'kg'
  const series = data.days.map((d) => ({
    ...d,
    label: shortDate(d.date),
    weight: toDisplayWeight(d.weight, units),
    weight_trend: toDisplayWeight(d.weight_trend, units),
  }))
  const hasWeights = series.some((d) => d.weight != null)
  const hasFood = series.some((d) => d.calories != null)
  const targets = data.targets

  return (
    <section className="charts" aria-label="Progress charts">
      <div className="range" role="group" aria-label="Date range">
        {RANGES.map((r) => (
          <button key={r} type="button" aria-pressed={days === r} onClick={() => setDays(r)}>{r} days</button>
        ))}
      </div>

      <div className="card chart-card">
        <h3>Weight trend <span className="muted">({unit})</span></h3>
        <p className="muted small">Dots are daily weigh-ins; the line is a 7-day moving average, which smooths out water-weight noise.</p>
        {hasWeights ? (
          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={series} margin={{ top: 8, right: 12, left: -8, bottom: 0 }}>
              <CartesianGrid stroke="var(--grid)" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 12 }} minTickGap={24} />
              <YAxis domain={['dataMin - 1', 'dataMax + 1']} tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="weight" name="Weigh-in" stroke="none" dot={{ r: 3.5, fill: 'var(--weight-dot)', stroke: 'none' }} activeDot={{ r: 5 }} isAnimationActive={false} />
              <Line type="monotone" dataKey="weight_trend" name="Trend" stroke="var(--accent)" strokeWidth={2.5} dot={false} connectNulls />
            </ComposedChart>
          </ResponsiveContainer>
        ) : <p className="empty">Log a weigh-in to start your trend line.</p>}
      </div>

      <div className="chart-pair">
        <div className="card chart-card">
          <h3>Calories <span className="muted">vs target</span></h3>
          {hasFood ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={series} margin={{ top: 8, right: 12, left: -8, bottom: 0 }}>
                <CartesianGrid stroke="var(--grid)" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} minTickGap={24} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="calories" name="Calories" fill="var(--cal)" radius={[3, 3, 0, 0]} />
                {targets && <ReferenceLine y={targets.calories.value} stroke="var(--ink)" strokeDasharray="4 4" label={{ value: 'target', position: 'insideTopRight', fontSize: 11 }} />}
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="empty">Log food to see daily calories.</p>}
        </div>
        <div className="card chart-card">
          <h3>Protein <span className="muted">vs target (g)</span></h3>
          {hasFood ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={series} margin={{ top: 8, right: 12, left: -8, bottom: 0 }}>
                <CartesianGrid stroke="var(--grid)" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} minTickGap={24} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="protein" name="Protein" fill="var(--protein)" radius={[3, 3, 0, 0]} />
                {targets && <ReferenceLine y={targets.protein.value} stroke="var(--ink)" strokeDasharray="4 4" label={{ value: 'target', position: 'insideTopRight', fontSize: 11 }} />}
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="empty">Log food to see daily protein.</p>}
        </div>
      </div>
    </section>
  )
}
