"""
Database layer — SQLite via SQLAlchemy
(upgrade path: swap DB_URL to TimescaleDB/PostgreSQL in config)
"""
import json
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Float, Integer, String, DateTime, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

engine = create_engine(
    settings.DB_URL,
    connect_args={"check_same_thread": False},
)
Session = sessionmaker(bind=engine)
Base    = declarative_base()


# ── Tables ─────────────────────────────────────────────────────────────────

class Candle(Base):
    """candles_1h — OHLCV hourly"""
    __tablename__ = "candles_1h"
    id     = Column(Integer, primary_key=True)
    ts     = Column(DateTime, index=True, nullable=False, unique=True)
    symbol = Column(String, default="XAUUSD")
    open   = Column(Float)
    high   = Column(Float)
    low    = Column(Float)
    close  = Column(Float)
    volume = Column(Float, default=0.0)


class Signal(Base):
    """signals — AI decisions"""
    __tablename__ = "signals"
    id            = Column(Integer, primary_key=True)
    ts            = Column(DateTime, default=datetime.utcnow, index=True)
    symbol        = Column(String, default="XAUUSD")
    bias          = Column(String)        # "buy" | "sell" | "neutral"
    confidence    = Column(Float)
    score         = Column(Float, default=0.0)
    model_version = Column(String, default="meta_v0")
    features_json = Column(Text, default="{}")


class BacktestResult(Base):
    """backtest_results — historical performance"""
    __tablename__ = "backtest_results"
    id            = Column(Integer, primary_key=True)
    run_ts        = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)
    start_date    = Column(String)
    end_date      = Column(String)
    metrics       = Column(Text)          # JSON


# ── Init ───────────────────────────────────────────────────────────────────

def init_db():
    settings.DATA_DIR.mkdir(exist_ok=True)
    settings.MODEL_DIR.mkdir(exist_ok=True)
    Base.metadata.create_all(engine)
