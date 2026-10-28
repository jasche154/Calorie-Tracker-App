from conftest import PROFILE


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_cors_allows_vite_dev_server(client):
    r = client.options(
        "/api/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_calculate_targets_is_stateless(client):
    r = client.post("/api/targets/calculate", json=PROFILE)
    assert r.status_code == 200
    assert {"calories", "protein"} <= r.json().keys()
    assert client.get("/api/profile").status_code == 404


def test_calculate_rejects_invalid_input(client):
    assert client.post("/api/targets/calculate", json={**PROFILE, "age": 5}).status_code == 422
    assert client.post("/api/targets/calculate", json={**PROFILE, "goal": "shred"}).status_code == 422


def test_save_and_update_profile(client):
    r = client.put("/api/profile", json=PROFILE)
    assert r.status_code == 200
    first_id = r.json()["profile"]["id"]
    r = client.put("/api/profile", json={**PROFILE, "goal": "bulk"})
    assert r.json()["profile"]["id"] == first_id
    assert client.get("/api/profile").json()["profile"]["goal"] == "bulk"
