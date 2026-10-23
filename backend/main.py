import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401  (registers tables on Base.metadata)
from database import Base, engine
from routers import foods, profile

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Calorie Tracker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(profile.router)
app.include_router(foods.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
