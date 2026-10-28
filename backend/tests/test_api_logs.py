from datetime import date, timedelta

from conftest import PROFILE


def test_food_log_scales_macros_and_totals(client):
    food = client.post("/api/foods", json={
        "name": "Chicken breast", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6,
    }).json()
    today = date.today().isoformat()
    r = client.post("/api/log", json={"date": today, "food_id": food["id"], "grams": 200})
    assert r.status_code == 201
    assert r.json()["calories"] == 330
    client.post("/api/log", json={"date": today, "food_id": food["id"], "grams": 100})

    day = client.get("/api/log", params={"date": today}).json()
    assert len(day["entries"]) == 2
    assert day["totals"]["protein"] == 93

    assert client.delete(f"/api/log/{r.json()['id']}").status_code == 204
    assert client.get("/api/log", params={"date": today}).json()["totals"]["calories"] == 165


def test_log_unknown_food_is_404(client):
    r = client.post("/api/log", json={"date": "2026-01-01", "food_id": 999, "grams": 100})
    assert r.status_code == 404


def test_weight_upserts_per_day_and_updates_profile(client):
    client.put("/api/profile", json=PROFILE)
    client.post("/api/weights", json={"date": "2026-10-01", "weight_kg": 80})
    client.post("/api/weights", json={"date": "2026-10-02", "weight_kg": 79.5})
    client.post("/api/weights", json={"date": "2026-10-02", "weight_kg": 79.0})
    weights = client.get("/api/weights").json()
    assert [w["weight_kg"] for w in weights] == [80, 79.0]
    assert client.get("/api/profile").json()["profile"]["weight_kg"] == 79.0

    # An older back-filled weigh-in must not overwrite the current weight.
    client.post("/api/weights", json={"date": "2026-09-01", "weight_kg": 85})
    assert client.get("/api/profile").json()["profile"]["weight_kg"] == 79.0


def test_progress_series_has_every_day_and_trend(client):
    client.put("/api/profile", json=PROFILE)
    end = date(2026, 10, 20)
    for i, kg in enumerate([80, 79.8, 79.6]):
        client.post("/api/weights", json={"date": (end - timedelta(days=2 - i)).isoformat(), "weight_kg": kg})
    food = client.post("/api/foods", json={
        "name": "Rice", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3,
    }).json()
    client.post("/api/log", json={"date": end.isoformat(), "food_id": food["id"], "grams": 300})

    p = client.get("/api/progress", params={"days": 7, "end": end.isoformat()}).json()
    assert len(p["days"]) == 7
    last = p["days"][-1]
    assert last["calories"] == 390
    assert last["weight"] == 79.6
    assert last["weight_trend"] == 79.8
    assert p["days"][0]["calories"] is None
    assert p["targets"]["calories"]["value"] > 0
