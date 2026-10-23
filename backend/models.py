from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

search_cache_foods = Table(
    "search_cache_foods",
    Base.metadata,
    Column("search_id", ForeignKey("search_cache.id"), primary_key=True),
    Column("food_id", ForeignKey("foods.id"), primary_key=True),
)


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    sex: Mapped[str] = mapped_column(String(10))
    age: Mapped[int] = mapped_column(Integer)
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    activity: Mapped[str] = mapped_column(String(20))
    goal: Mapped[str] = mapped_column(String(10))
    pace: Mapped[str] = mapped_column(String(12), default="moderate")


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    brand: Mapped[str | None] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(20), default="openfoodfacts")
    # All nutrient values are per 100 g.
    calories: Mapped[float] = mapped_column(Float, default=0)
    protein: Mapped[float] = mapped_column(Float, default=0)
    carbs: Mapped[float] = mapped_column(Float, default=0)
    fat: Mapped[float] = mapped_column(Float, default=0)
    fiber: Mapped[float] = mapped_column(Float, default=0)


class SearchCache(Base):
    __tablename__ = "search_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    foods: Mapped[list[Food]] = relationship(secondary=search_cache_foods)


class FoodLog(Base):
    __tablename__ = "food_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"))
    grams: Mapped[float] = mapped_column(Float)
    food: Mapped[Food] = relationship()


class WeightEntry(Base):
    __tablename__ = "weights"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    weight_kg: Mapped[float] = mapped_column(Float)
