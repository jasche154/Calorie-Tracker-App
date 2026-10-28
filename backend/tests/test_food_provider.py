import httpx
import pytest

import food_provider
from food_provider import FoodProviderError, search_open_food_facts


def fake_get(payload=None, status=200, exc=None):
    def _get(url, **kwargs):
        if exc:
            raise exc
        return httpx.Response(status, json=payload, request=httpx.Request("GET", url))
    return _get


def test_parses_products_and_skips_incomplete_or_duplicate(monkeypatch):
    payload = {"products": [
        {"code": "1", "product_name": "Oats", "brands": "Quaker, PepsiCo",
         "nutriments": {"energy-kcal_100g": "379", "proteins_100g": 13.0423529, "fiber_100g": 10,
                        "fat_100g": "n/a"}},
        {"code": "1", "product_name": "Oats", "nutriments": {"energy-kcal_100g": 379}},
        {"code": "2", "product_name": "", "nutriments": {"energy-kcal_100g": 100}},
        {"code": "3", "product_name": "No kcal", "nutriments": {}},
    ]}
    monkeypatch.setattr(food_provider.httpx, "get", fake_get(payload))
    results = search_open_food_facts("oats")
    assert len(results) == 1
    assert results[0] == {
        "external_id": "off:1", "name": "Oats", "brand": "Quaker", "calories": 379.0,
        "protein": 13.0, "carbs": 0.0, "fat": 0.0, "fiber": 10.0,
    }


@pytest.mark.parametrize("kwargs", [
    {"status": 503, "payload": {}},
    {"exc": httpx.ConnectTimeout("timeout")},
])
def test_network_errors_raise_provider_error(monkeypatch, kwargs):
    monkeypatch.setattr(food_provider.httpx, "get", fake_get(**kwargs))
    with pytest.raises(FoodProviderError):
        search_open_food_facts("oats")
