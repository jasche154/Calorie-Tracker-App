# Calorie Tracker — Initial Plan

A MacroFactor-style calorie/macro tracker. FastAPI + SQLite backend, React (Vite) frontend with Recharts.

## Issues found in the starting skeleton

| # | Issue | Fix |
|---|-------|-----|
| 1 | No `requirements.txt` — the venv can't be recreated by anyone else | Added `backend/requirements.txt` |
| 2 | No CORS middleware — a React dev server on another port is blocked by the browser | Added `CORSMiddleware` for the Vite origin |
| 3 | `.gitignore` misses `node_modules/`, `*.db`, `.env`, nested `__pycache__/`, `.pytest_cache/` | Expanded `.gitignore` |
| 4 | venv is Python 3.11, system Python is 3.13 — commands run without the venv pick different package versions (FastAPI 0.141 vs 0.124) | Documented: always use `backend/venv` |
| 5 | venv has both `dotenv` (a shim package) and `python-dotenv` — easy to confuse; only `python-dotenv` is needed | Not used by the new code; `requirements.txt` lists neither |
| 6 | `frontend/` was empty (git doesn't track empty dirs, so it never reached the repo) | Scaffolded with Vite |
| 7 | Root route only, no `/api` prefix or health check; missing newline at EOF | Rebuilt `main.py` with routers under `/api` |

## Features (priority order)

1. **Onboarding / targets** — enter sex, age, height, weight, activity level, goal (cut / maintain / bulk) and pace.
   - BMR: Mifflin-St Jeor. TDEE = BMR × activity multiplier.
   - Goal: cut = −(pace × 7700 kcal/kg ÷ 7) per day, bulk = + surplus. Floor at a safe minimum (1200 F / 1500 M).
   - **Calories + protein are the headline numbers.** Protein: 2.2 g/kg on a cut, 1.8 g/kg on bulk/maintain.
   - Secondary: fat, carbs, fiber, water, BMI, TDEE, BMR, projected weekly change.
   - Every metric carries a `why` string; the UI shows it on hover.
2. **Food search with a local cache** — search Open Food Facts (free, no key). The first search for a query hits the API and saves every product + the query→product mapping in SQLite. The same (normalized) query afterwards is served from the DB with no API call. Response says `source: "cache" | "api"`.
3. **Food log** — add a food with grams eaten; macros scaled from per-100 g values. Daily totals vs targets.
4. **Weight log** — daily weigh-ins.
5. **Progress charts** — weight trend (raw + 7-day moving average), daily calories vs target, daily protein vs target.
6. **Image import (experimental, later)** — stubbed `POST /api/foods/recognize` returning 501 with the design notes in `NOTES.md`.

## Architecture

```
backend/
  main.py            app + CORS + routers
  database.py        engine/session (SQLite file, overridable for tests)
  models.py          SQLAlchemy: Profile, Food, SearchCache, FoodLog, WeightEntry
  schemas.py         Pydantic in/out models
  calculator.py      pure TDEE/macro math (no I/O)
  food_provider.py   Open Food Facts client (injectable for tests)
  routers/           profile, foods, logs, progress
  tests/             pytest: calculator unit tests + API integration tests (API mocked)
frontend/
  src/api.js         fetch wrapper
  src/components/    Onboarding, Targets (with tooltips), FoodSearch, DailyLog, WeightLog, Charts
```

## Testing

- `pytest` — calculator math, cache hit/miss behavior (provider mocked, asserts it is called once), log CRUD, progress aggregation.
- Browser run-through of onboarding → search → log → charts.
