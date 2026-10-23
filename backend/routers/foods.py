import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from food_provider import FoodProviderError, get_food_provider
from models import Food, SearchCache
from schemas import FoodIn, FoodOut, SearchResult

router = APIRouter(prefix="/api/foods", tags=["foods"])

LOCAL_FALLBACK_LIMIT = 20


def normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", query.strip().lower())


def upsert_food(db: Session, data: dict) -> Food:
    existing = db.query(Food).filter_by(external_id=data["external_id"]).first()
    if existing:
        return existing
    food = Food(**data, source="openfoodfacts")
    db.add(food)
    return food


@router.get("/search", response_model=SearchResult)
def search_foods(
    q: str = Query(min_length=2, max_length=100),
    db: Session = Depends(get_db),
    provider=Depends(get_food_provider),
):
    """Serve from the local cache when this query was searched before; otherwise
    call the external API once and store the products + query for next time."""
    query = normalize_query(q)
    cached = db.query(SearchCache).filter_by(query=query).first()
    if cached:
        return {"query": query, "source": "cache", "results": cached.foods}

    try:
        found = provider(query)
    except FoodProviderError:
        # API down — fall back to whatever matching foods we already have locally.
        local = (
            db.query(Food)
            .filter(Food.name.ilike(f"%{query}%"))
            .limit(LOCAL_FALLBACK_LIMIT)
            .all()
        )
        if local:
            return {"query": query, "source": "local", "results": local}
        raise HTTPException(status_code=502, detail="Food database is unavailable, try again shortly")

    foods = [upsert_food(db, item) for item in found]
    db.add(SearchCache(query=query, foods=foods))
    db.commit()
    return {"query": query, "source": "api", "results": foods}


@router.post("", response_model=FoodOut, status_code=201)
def create_custom_food(body: FoodIn, db: Session = Depends(get_db)):
    food = Food(**body.model_dump(), source="custom")
    db.add(food)
    db.commit()
    db.refresh(food)
    return food


@router.post("/recognize", status_code=501)
def recognize_food_image():
    """Experimental, not implemented yet — see NOTES.md for the design."""
    raise HTTPException(status_code=501, detail="Image recognition is planned but not implemented yet")
