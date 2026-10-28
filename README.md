# Fuellog — Calorie Tracker

A MacroFactor-style calorie and macro tracker. FastAPI + SQLite backend, React + Recharts frontend.

- Enter height, weight, age, activity and goal (lose fat / maintain / build muscle) to get calorie and protein targets, plus fat, carbs, fiber, water, BMR, TDEE and BMI. Hover over any number to see why it matters.
- Search foods from Open Food Facts. Each search is saved locally, so repeating a search makes no API call.
- Log food by grams and log daily weigh-ins. Your latest weigh-in updates your targets.
- Progress charts: weight with a 7-day trend line, and daily calories and protein against your targets.

## Setup

```bash
# backend (Python 3.11 venv lives in backend/venv)
cd backend
python -m venv venv                         # only if venv/ doesn't exist
venv/Scripts/python -m pip install -r requirements.txt
venv/Scripts/python -m uvicorn main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev                                 # http://localhost:5173
```

## Tests

```bash
cd backend && venv/Scripts/python -m pytest tests -q --cov=.
cd frontend && npx oxlint src && npm run build
```

See `PLAN.md` for the design and `NOTES.md` for status, decisions and next steps.
