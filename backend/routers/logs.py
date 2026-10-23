from datetime import date as Date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from calculator import calculate_targets, scale_nutrients
from database import get_db
from models import Food, FoodLog, Profile, WeightEntry
from schemas import LogIn, ProfileIn, WeightIn, WeightOut

router = APIRouter(prefix="/api", tags=["logs"])

NUTRIENTS = ("calories", "protein", "carbs", "fat", "fiber")
TREND_WINDOW_DAYS = 7


def entry_to_dict(entry: FoodLog) -> dict:
    per_100g = {k: getattr(entry.food, k) for k in NUTRIENTS}
    return {
        "id": entry.id,
        "date": entry.date.isoformat(),
        "grams": entry.grams,
        "food": {"id": entry.food.id, "name": entry.food.name, "brand": entry.food.brand},
        **scale_nutrients(per_100g, entry.grams),
    }


def sum_nutrients(entries: list[dict]) -> dict:
    return {k: round(sum(e[k] for e in entries), 1) for k in NUTRIENTS}


@router.get("/log")
def read_log(date: Date, db: Session = Depends(get_db)) -> dict:
    entries = [entry_to_dict(e) for e in db.query(FoodLog).filter_by(date=date).order_by(FoodLog.id)]
    return {"date": date.isoformat(), "entries": entries, "totals": sum_nutrients(entries)}


@router.post("/log", status_code=201)
def add_log_entry(body: LogIn, db: Session = Depends(get_db)) -> dict:
    if db.get(Food, body.food_id) is None:
        raise HTTPException(status_code=404, detail="Food not found")
    entry = FoodLog(**body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry_to_dict(entry)


@router.delete("/log/{entry_id}", status_code=204)
def delete_log_entry(entry_id: int, db: Session = Depends(get_db)) -> None:
    entry = db.get(FoodLog, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Log entry not found")
    db.delete(entry)
    db.commit()


@router.get("/weights", response_model=list[WeightOut])
def list_weights(db: Session = Depends(get_db)):
    return db.query(WeightEntry).order_by(WeightEntry.date).all()


@router.post("/weights", response_model=WeightOut, status_code=201)
def log_weight(body: WeightIn, db: Session = Depends(get_db)):
    """One weigh-in per day (re-posting a date overwrites it). The latest weigh-in
    also updates the profile so calorie targets follow your current weight."""
    entry = db.query(WeightEntry).filter_by(date=body.date).first()
    if entry is None:
        entry = WeightEntry(**body.model_dump())
        db.add(entry)
    else:
        entry.weight_kg = body.weight_kg

    latest = db.query(WeightEntry).order_by(WeightEntry.date.desc()).first()
    profile = db.query(Profile).first()
    if profile and (latest is None or body.date >= latest.date):
        profile.weight_kg = body.weight_kg
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/weights/{weight_id}", status_code=204)
def delete_weight(weight_id: int, db: Session = Depends(get_db)) -> None:
    entry = db.get(WeightEntry, weight_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Weight entry not found")
    db.delete(entry)
    db.commit()


def moving_average(values: list[float | None], window: int) -> list[float | None]:
    """Trailing average over the last `window` days that have a value."""
    result = []
    for i in range(len(values)):
        recent = [v for v in values[max(0, i - window + 1): i + 1] if v is not None]
        result.append(round(sum(recent) / len(recent), 2) if recent else None)
    return result


@router.get("/progress")
def progress(
    days: int = Query(default=30, ge=7, le=365),
    end: Date | None = None,
    db: Session = Depends(get_db),
) -> dict:
    end = end or Date.today()
    start = end - timedelta(days=days - 1)

    by_day: dict[Date, list[dict]] = {}
    for e in db.query(FoodLog).filter(FoodLog.date.between(start, end)):
        by_day.setdefault(e.date, []).append(entry_to_dict(e))
    weights = {
        w.date: w.weight_kg
        for w in db.query(WeightEntry).filter(WeightEntry.date.between(start, end))
    }

    dates = [start + timedelta(days=i) for i in range(days)]
    weight_series = [weights.get(d) for d in dates]
    trend = moving_average(weight_series, TREND_WINDOW_DAYS)
    series = [
        {
            "date": d.isoformat(),
            **(sum_nutrients(by_day[d]) if d in by_day else {k: None for k in NUTRIENTS}),
            "weight": weight_series[i],
            "weight_trend": trend[i],
        }
        for i, d in enumerate(dates)
    ]

    profile = db.query(Profile).first()
    targets = None
    if profile:
        targets = calculate_targets(**ProfileIn.model_validate(profile, from_attributes=True).model_dump())
    return {"start": start.isoformat(), "end": end.isoformat(), "days": series, "targets": targets}
