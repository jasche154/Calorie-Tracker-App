from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from calculator import calculate_targets
from database import get_db
from models import Profile
from schemas import ProfileIn, ProfileOut

router = APIRouter(prefix="/api", tags=["profile"])


def get_profile(db: Session) -> Profile | None:
    return db.query(Profile).first()


@router.post("/targets/calculate")
def calculate(body: ProfileIn) -> dict:
    """Stateless estimate — used by onboarding before anything is saved."""
    return calculate_targets(**body.model_dump())


@router.get("/profile")
def read_profile(db: Session = Depends(get_db)) -> dict:
    profile = get_profile(db)
    if profile is None:
        raise HTTPException(status_code=404, detail="No profile yet")
    data = ProfileIn.model_validate(profile, from_attributes=True)
    return {
        "profile": ProfileOut.model_validate(profile).model_dump(),
        "targets": calculate_targets(**data.model_dump()),
    }


@router.put("/profile")
def save_profile(body: ProfileIn, db: Session = Depends(get_db)) -> dict:
    profile = get_profile(db)
    if profile is None:
        profile = Profile(**body.model_dump())
        db.add(profile)
    else:
        for key, value in body.model_dump().items():
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return {
        "profile": ProfileOut.model_validate(profile).model_dump(),
        "targets": calculate_targets(**body.model_dump()),
    }
