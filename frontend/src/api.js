async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })
  if (res.status === 204) return null
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => `${d.loc?.at(-1)}: ${d.msg}`).join(', ')
      : data.detail
    const error = new Error(detail || `Request failed (${res.status})`)
    error.status = res.status
    throw error
  }
  return data
}

export const api = {
  calculate: (profile) => request('/targets/calculate', { method: 'POST', body: profile }),
  getProfile: () => request('/profile'),
  saveProfile: (profile) => request('/profile', { method: 'PUT', body: profile }),
  searchFoods: (q) => request(`/foods/search?q=${encodeURIComponent(q)}`),
  createFood: (food) => request('/foods', { method: 'POST', body: food }),
  getLog: (date) => request(`/log?date=${date}`),
  addLog: (entry) => request('/log', { method: 'POST', body: entry }),
  deleteLog: (id) => request(`/log/${id}`, { method: 'DELETE' }),
  getWeights: () => request('/weights'),
  addWeight: (entry) => request('/weights', { method: 'POST', body: entry }),
  deleteWeight: (id) => request(`/weights/${id}`, { method: 'DELETE' }),
  getProgress: (days) => request(`/progress?days=${days}&end=${today()}`),
}

export const LB_PER_KG = 2.20462
export const CM_PER_IN = 2.54

export function today() {
  const d = new Date()
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10)
}

export const toDisplayWeight = (kg, units) =>
  kg == null ? null : Math.round((units === 'imperial' ? kg * LB_PER_KG : kg) * 10) / 10

export const toKg = (value, units) => (units === 'imperial' ? value / LB_PER_KG : value)
