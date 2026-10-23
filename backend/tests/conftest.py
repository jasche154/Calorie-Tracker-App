import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DATABASE_URL", "sqlite://")

from database import Base, get_db  # noqa: E402
from food_provider import FoodProviderError, get_food_provider  # noqa: E402
from main import app  # noqa: E402

FAKE_FOODS = [
    {"external_id": "off:1", "name": "Greek Yogurt", "brand": "Fage", "calories": 97,
     "protein": 9, "carbs": 3.9, "fat": 5, "fiber": 0},
    {"external_id": "off:2", "name": "Greek Yogurt 0%", "brand": "Chobani", "calories": 59,
     "protein": 10, "carbs": 3.6, "fat": 0.4, "fiber": 0},
]


class FakeProvider:
    def __init__(self):
        self.calls: list[str] = []
        self.fail = False

    def __call__(self, query: str) -> list[dict]:
        self.calls.append(query)
        if self.fail:
            raise FoodProviderError("down")
        return [dict(f) for f in FAKE_FOODS]


@pytest.fixture
def provider():
    return FakeProvider()


@pytest.fixture
def client(provider):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_food_provider] = lambda: provider
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


PROFILE = {
    "sex": "male", "age": 30, "height_cm": 180, "weight_kg": 80,
    "activity": "moderate", "goal": "cut", "pace": "moderate",
}
