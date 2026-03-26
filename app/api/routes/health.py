from fastapi import APIRouter
from datetime import datetime
from ...core.database import Session, Candle, Signal
from ...models.gold_ohlcv_model import ohlcv_model

router = APIRouter()


@router.get("/health")
def health():
    if ohlcv_model.is_trained and not ohlcv_model.metrics:
        ohlcv_model.load()
    session = Session()
    try:
        n_candles = session.query(Candle).count()
        n_signals = session.query(Signal).count()
        last      = session.query(Candle).order_by(Candle.ts.desc()).first()
    finally:
        session.close()

    return {
        "status":    "ok",
        "ts":        datetime.utcnow().isoformat(),
        "database": {
            "candles": n_candles,
            "signals": n_signals,
            "last_candle_ts": last.ts.isoformat() if last else None,
        },
        "models": {
            "ohlcv_v0": {
                "trained": ohlcv_model.is_trained,
                "metrics": ohlcv_model.metrics,
            },
            # "orderflow_v0": {"trained": of_model.is_trained},  # Phase 5
            # "smc_v0":       {"trained": smc_model.is_trained}, # Phase 6
        },
    }
