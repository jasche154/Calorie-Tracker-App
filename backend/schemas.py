from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Sex = Literal["male", "female"]
Activity = Literal["sedentary", "light", "moderate", "active", "very_active"]
Goal = Literal["cut", "maintain", "bulk"]
Pace = Literal["slow", "moderate", "aggressive"]


class ProfileIn(BaseModel):
    sex: Sex
    age: int = Field(ge=13, le=100)
    height_cm: float = Field(ge=100, le=250)
    weight_kg: float = Field(ge=30, le=350)
    activity: Activity
    goal: Goal
    pace: Pace = "moderate"


class ProfileOut(ProfileIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FoodIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    brand: str | None = Field(default=None, max_length=200)
    calories: float = Field(ge=0, le=900)
    protein: float = Field(ge=0, le=100)
    carbs: float = Field(ge=0, le=100)
    fat: float = Field(ge=0, le=100)
    fiber: float = Field(default=0, ge=0, le=100)


class FoodOut(FoodIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source: str


class SearchResult(BaseModel):
    query: str
    source: Literal["cache", "api", "local"]
    results: list[FoodOut]


class LogIn(BaseModel):
    date: Date
    food_id: int
    grams: float = Field(gt=0, le=5000)


class WeightIn(BaseModel):
    date: Date
    weight_kg: float = Field(ge=30, le=350)


class WeightOut(WeightIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
