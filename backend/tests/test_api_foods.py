def test_search_calls_api_once_then_uses_cache(client, provider):
    first = client.get("/api/foods/search", params={"q": "Greek Yogurt"}).json()
    assert first["source"] == "api"
    assert len(first["results"]) == 2

    # Different casing/whitespace is the same normalized query.
    second = client.get("/api/foods/search", params={"q": "  greek   YOGURT "}).json()
    assert second["source"] == "cache"
    assert [f["id"] for f in second["results"]] == [f["id"] for f in first["results"]]
    assert provider.calls == ["greek yogurt"]


def test_overlapping_searches_do_not_duplicate_foods(client, provider):
    a = client.get("/api/foods/search", params={"q": "yogurt"}).json()
    b = client.get("/api/foods/search", params={"q": "greek yogurt"}).json()
    assert {f["id"] for f in a["results"]} == {f["id"] for f in b["results"]}
    assert len(provider.calls) == 2


def test_search_falls_back_to_local_db_when_api_down(client, provider):
    client.get("/api/foods/search", params={"q": "greek yogurt"})
    provider.fail = True
    r = client.get("/api/foods/search", params={"q": "yogurt"})
    assert r.status_code == 200
    assert r.json()["source"] == "local"


def test_search_returns_502_when_api_down_and_nothing_local(client, provider):
    provider.fail = True
    assert client.get("/api/foods/search", params={"q": "pizza"}).status_code == 502


def test_search_rejects_too_short_query(client):
    assert client.get("/api/foods/search", params={"q": "a"}).status_code == 422


def test_image_recognition_is_stubbed(client):
    assert client.post("/api/foods/recognize").status_code == 501


def test_create_custom_food(client):
    r = client.post("/api/foods", json={
        "name": "Chicken breast", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6,
    })
    assert r.status_code == 201
    assert r.json()["source"] == "custom"
