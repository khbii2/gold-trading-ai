"""
Gold Trading AI — FastAPI Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import init_db
from .api.routes import signals, health, ui, live


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    init_db()
    print("[startup] DB ready — call POST /api/v1/model/train to train the model")
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────


app = FastAPI(
    title       = "Gold Trading AI",
    version     = "0.1.0",
    description = "Professional XAUUSD trading AI — OHLCV v0 → Order Flow → SMC → Meta",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

app.include_router(ui.router,        tags=["ui"])
app.include_router(health.router,    tags=["health"])
app.include_router(live.router,      prefix="/api/v1", tags=["live"])
app.include_router(signals.router,   prefix="/api/v1", tags=["signals"])
