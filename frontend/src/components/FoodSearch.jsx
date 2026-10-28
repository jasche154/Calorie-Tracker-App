import { useState } from 'react'
import { api } from '../api'

const SOURCE_LABEL = {
  cache: 'Served from your local database — no API call',
  api: 'Fetched from Open Food Facts and saved for next time',
  local: 'Food API unavailable — showing matches already in your database',
}

function ResultRow({ food, onAdd }) {
  const [grams, setGrams] = useState(100)
  return (
    <li className="food-row">
      <div className="food-row__info">
        <strong>{food.name}</strong>
        {food.brand && <span className="muted"> · {food.brand}</span>}
        <div className="macros">
          {Math.round(food.calories)} kcal · P {+food.protein.toFixed(1)}g · C {+food.carbs.toFixed(1)}g · F {+food.fat.toFixed(1)}g
          <span className="muted"> per 100 g</span>
        </div>
      </div>
      <form className="food-row__add" onSubmit={(e) => { e.preventDefault(); onAdd(food, Number(grams)) }}>
        <input
          type="number" min="1" max="5000" value={grams} aria-label={`Grams of ${food.name}`}
          onChange={(e) => setGrams(e.target.value)}
        />
        <span>g</span>
        <button type="submit">Add</button>
      </form>
    </li>
  )
}

const EMPTY_CUSTOM = { name: '', calories: '', protein: '', carbs: '', fat: '' }

export default function FoodSearch({ date, onLogged }) {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [custom, setCustom] = useState(null)

  async function handleSearch(e) {
    e.preventDefault()
    if (query.trim().length < 2) return
    setError('')
    setIsLoading(true)
    try {
      setResult(await api.searchFoods(query))
    } catch (err) {
      setError(err.message)
      setResult(null)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleAdd(food, grams) {
    try {
      await api.addLog({ date, food_id: food.id, grams })
      onLogged()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleCustom(e) {
    e.preventDefault()
    try {
      const food = await api.createFood({
        name: custom.name,
        calories: Number(custom.calories),
        protein: Number(custom.protein || 0),
        carbs: Number(custom.carbs || 0),
        fat: Number(custom.fat || 0),
      })
      setResult({ query: food.name, source: 'cache', results: [food], isCustom: true })
      setCustom(null)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <section className="card" aria-labelledby="search-heading">
      <h2 id="search-heading">Add food</h2>
      <form className="search" onSubmit={handleSearch}>
        <input
          type="search" placeholder="Search foods, e.g. greek yogurt" value={query}
          onChange={(e) => setQuery(e.target.value)} aria-label="Search foods"
        />
        <button type="submit" disabled={isLoading}>{isLoading ? 'Searching…' : 'Search'}</button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}
      {result && !result.isCustom && (
        <p className={`source source--${result.source}`} data-testid="search-source">
          {SOURCE_LABEL[result.source]}
        </p>
      )}
      {result && result.results.length === 0 && <p className="muted">No foods found. Try a simpler term or add it yourself.</p>}
      {result && (
        <ul className="food-list">
          {result.results.map((f) => <ResultRow key={f.id} food={f} onAdd={handleAdd} />)}
        </ul>
      )}

      {custom ? (
        <form className="custom-food" onSubmit={handleCustom}>
          <input required placeholder="Food name" value={custom.name} onChange={(e) => setCustom({ ...custom, name: e.target.value })} />
          {['calories', 'protein', 'carbs', 'fat'].map((k) => (
            <input
              key={k} type="number" min="0" step="0.1" required={k === 'calories'}
              placeholder={`${k} /100g`} value={custom[k]}
              onChange={(e) => setCustom({ ...custom, [k]: e.target.value })}
            />
          ))}
          <button type="submit">Save food</button>
          <button type="button" className="ghost" onClick={() => setCustom(null)}>Cancel</button>
        </form>
      ) : (
        <button type="button" className="ghost" onClick={() => setCustom(EMPTY_CUSTOM)}>+ Create custom food</button>
      )}
      <p className="muted small">📷 Photo logging (computer vision) is planned as an experimental feature.</p>
    </section>
  )
}
