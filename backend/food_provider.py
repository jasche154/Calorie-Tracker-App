"""External food database client (Open Food Facts — free, no API key)."""

import logging

import httpx

logger = logging.getLogger(__name__)

OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
OFF_FIELDS = "code,product_name,brands,nutriments"
PAGE_SIZE = 20
TIMEOUT_SECONDS = 15
USER_AGENT = "CalorieTrackerApp/0.1 (student project)"


class FoodProviderError(Exception):
    pass


def _num(value) -> float:
    """OFF values are sometimes strings or long floats (10.5882352941176)."""
    try:
        return round(float(value or 0), 1)
    except (TypeError, ValueError):
        return 0.0


def _parse_product(product: dict) -> dict | None:
    name = (product.get("product_name") or "").strip()
    nutriments = product.get("nutriments") or {}
    kcal = nutriments.get("energy-kcal_100g")
    if not name or kcal is None:
        return None
    return {
        "external_id": f"off:{product.get('code')}",
        "name": name[:200],
        "brand": (product.get("brands") or "").split(",")[0].strip()[:200] or None,
        "calories": _num(kcal),
        "protein": _num(nutriments.get("proteins_100g")),
        "carbs": _num(nutriments.get("carbohydrates_100g")),
        "fat": _num(nutriments.get("fat_100g")),
        "fiber": _num(nutriments.get("fiber_100g")),
    }


def search_open_food_facts(query: str) -> list[dict]:
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": PAGE_SIZE,
        "fields": OFF_FIELDS,
    }
    try:
        resp = httpx.get(
            OFF_SEARCH_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        products = resp.json().get("products", [])
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Open Food Facts search failed for %r: %s", query, exc)
        raise FoodProviderError(str(exc)) from exc

    parsed = (_parse_product(p) for p in products)
    seen: set[str] = set()
    results = []
    for food in parsed:
        if food and food["external_id"] not in seen:
            seen.add(food["external_id"])
            results.append(food)
    return results


def get_food_provider():
    """FastAPI dependency so tests can swap in a fake provider."""
    return search_open_food_facts
