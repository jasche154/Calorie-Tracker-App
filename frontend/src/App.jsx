import { useCallback, useEffect, useState } from 'react'
import { api, today } from './api'
import Charts from './components/Charts'
import DailyLog from './components/DailyLog'
import FoodSearch from './components/FoodSearch'
import ProfileForm from './components/ProfileForm'
import Targets from './components/Targets'
import WeightLog from './components/WeightLog'
import './App.css'

const UNITS_KEY = 'calorie-tracker-units'

function loadUnits() {
  try {
    return localStorage.getItem(UNITS_KEY) || 'imperial'
  } catch {
    return 'imperial'
  }
}

export default function App() {
  const [status, setStatus] = useState('loading') // loading | onboarding | ready | error
  const [profile, setProfile] = useState(null)
  const [targets, setTargets] = useState(null)
  const [units, setUnitsState] = useState(loadUnits)
  const [tab, setTab] = useState('today')
  const [log, setLog] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [error, setError] = useState('')
  const date = today()

  const setUnits = (u) => {
    setUnitsState(u)
    try { localStorage.setItem(UNITS_KEY, u) } catch { /* storage unavailable: keep in memory */ }
  }

  const applyProfile = ({ profile: p, targets: t }) => {
    setProfile(p)
    setTargets(t)
    setStatus('ready')
  }

  const refreshLog = useCallback(() => {
    api.getLog(date).then(setLog).catch((err) => setError(err.message))
    setRefreshKey((k) => k + 1)
  }, [date])

  useEffect(() => {
    api.getProfile()
      .then(applyProfile)
      .catch((err) => {
        if (err.status === 404) setStatus('onboarding')
        else { setError(err.message); setStatus('error') }
      })
  }, [])

  useEffect(() => {
    if (status === 'ready') api.getLog(date).then(setLog).catch((err) => setError(err.message))
  }, [status, date])

  const handleWeightLogged = async () => {
    applyProfile(await api.getProfile())
    setRefreshKey((k) => k + 1)
  }

  if (status === 'loading') return <main className="shell"><p className="muted">Loading…</p></main>
  if (status === 'error') {
    return (
      <main className="shell">
        <p className="error" role="alert">Can't reach the API: {error}. Is the backend running on port 8000?</p>
      </main>
    )
  }

  return (
    <main className="shell">
      <header className="masthead">
        <h1>Fuel<span>log</span></h1>
        {status === 'ready' && (
          <nav aria-label="Sections" className="tabs">
            {[['today', 'Today'], ['progress', 'Progress'], ['profile', 'Targets']].map(([k, l]) => (
              <button key={k} type="button" aria-pressed={tab === k} onClick={() => setTab(k)}>{l}</button>
            ))}
          </nav>
        )}
      </header>

      {status === 'onboarding' && (
        <ProfileForm profile={null} units={units} setUnits={setUnits} onSaved={applyProfile} />
      )}

      {status === 'ready' && tab === 'today' && (
        <div className="today">
          <div className="today__main">
            {log && <DailyLog log={log} targets={targets} onChanged={refreshLog} />}
            <FoodSearch date={date} onLogged={refreshLog} />
          </div>
          <aside className="today__side">
            <WeightLog units={units} onLogged={handleWeightLogged} />
            <Targets targets={targets} units={units} />
          </aside>
        </div>
      )}

      {status === 'ready' && tab === 'progress' && <Charts units={units} refreshKey={refreshKey} />}

      {status === 'ready' && tab === 'profile' && (
        <ProfileForm
          key={profile.id + profile.weight_kg}
          profile={profile} units={units} setUnits={setUnits}
          onSaved={(data) => { applyProfile(data); setTab('today') }}
        />
      )}
      {error && status === 'ready' && <p className="error" role="alert">{error}</p>}
    </main>
  )
}
