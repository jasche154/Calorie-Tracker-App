# Handoff Notes — session 2026-10-22 (20:40–20:58)

Context for whoever picks this up next. See `PLAN.md` for the original plan and the list of bugs found in the starting skeleton.

## Status: working MVP, everything tested

| Area | State |
|------|-------|
| Onboarding (sex/age/height/weight/activity/goal/pace → targets) | Done, imperial + metric |
| Calories + protein as headline numbers, 8 secondary metrics | Done |
| Hover/focus tooltips explaining each metric | Done (`Metric.jsx`, text lives in `calculator.WHY`) |
| Food search with SQLite cache (1 API call per unique query) | Done — `routers/foods.py` |
| Food log, daily totals vs targets | Done |
| Weigh-ins (latest one updates profile + targets) | Done |
| Charts: weight + 7-day trend, calories vs target, protein vs target (7/30/90 days) | Done (Recharts) |
| Image recognition | Stub only: `POST /api/foods/recognize` → 501 |

**Tests:** 28 pytest tests (calculator, API, cache hit/miss, provider parsing). Run: `cd backend && venv/Scripts/python -m pytest tests -q`.
**Manual browser test done:** onboarding → save → search (cache hit shown) → log 200 g → weigh-in → targets update → progress charts → phone width (375 px) has no horizontal scroll.
**Live API check:** first `greek yogurt` search 1.7 s from Open Food Facts, second 0.2 s from cache.

## Bugs found and fixed during the build
1. **Calorie floor turned a cut into a surplus.** For someone whose maintenance is below 1200/1500 kcal, the floor pushed "cut" calories above maintenance. Now the floor is capped at TDEE (`calculator.py`, regression test `test_floor_never_turns_a_cut_into_a_surplus`).
2. **SQLite path depended on the working directory**, so starting uvicorn from the repo root vs `backend/` created two different DBs. Now anchored to `backend/calorie_tracker.db`.
3. **Unrounded API values** (`10.5882352941176g`) shown in search results. Rounded at parse time; non-numeric values like `"n/a"` become 0.
4. **Weigh-in dots invisible** on the weight chart (Recharts default white fill).
5. **Hidden tooltips caused horizontal page scroll** at desktop width. Right-column tooltips now open leftward.

## Design decisions
- **Formula:** Mifflin-St Jeor BMR × activity multiplier. Cut/bulk pace is % of bodyweight per week (cut 0.25/0.5/1%, bulk 0.1/0.25/0.5%) × 7700 kcal/kg. Floor 1200 F / 1500 M (never above TDEE).
- **Protein:** 2.2 g/kg on a cut, 1.8 g/kg otherwise. **Fat:** 27% of calories. **Carbs:** remainder.
- **Cache key:** query lowercased with whitespace collapsed. Foods are de-duplicated by `external_id`, so overlapping queries share rows. If the API is down, the search falls back to a `LIKE` match on foods already stored (`source: "local"`).
- **Single-user app**: one `Profile` row, no auth. That is fine for a class project; it needs auth before it's deployed anywhere public.
- Vite proxies `/api` to `127.0.0.1:8000`, so CORS only matters if the frontend is served from elsewhere (`FRONTEND_ORIGINS` env var).

## Next steps (priority order)
1. **Adaptive TDEE (the MacroFactor feature):** once there are 2+ weeks of weigh-ins and food logs, estimate real maintenance as `avg intake − (trend weight change × 7700 / days)` and blend it with the formula estimate. `/api/progress` already returns the inputs (`weight_trend`, daily `calories`).
2. Serving sizes from OFF (`serving_size` field) so people can log "1 cup" rather than grams.
3. Cache expiry or refresh for stale searches (`SearchCache.created_at` already stored).
4. Barcode lookup: OFF supports `/api/v2/product/{barcode}`; it fits the same `Food.external_id` scheme.
5. Frontend tests (Vitest + Testing Library) and a Playwright e2e test for the onboarding → log → chart flow. Only manual browser testing so far.
6. Optional: migrate `.jsx` to `.tsx` (the Vite template was JS; kept it for speed).

## Experimental: photo → food (future)
Proposed design for `POST /api/foods/recognize`:
1. Accept a multipart image upload, with size/type validation (≤5 MB, jpeg/png/webp).
2. Send it to a vision model (e.g. Claude with an image block) and ask for structured JSON: `[{name, estimated_grams, confidence}]`.
3. For each item, run the existing cached `search_foods(name)` to get nutrients, so the vision model only identifies the food and the database supplies the numbers.
4. Return the candidates for the user to **confirm/edit before logging**. Never auto-log, because portion estimates from photos are rough.
5. The API key goes in `.env` (already gitignored), loaded at startup.

## How to run
```
cd backend && venv/Scripts/python -m uvicorn main:app --reload --port 8000
cd frontend && npm run dev     # http://localhost:5173
```
