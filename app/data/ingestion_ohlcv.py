"""
Data Ingestion — OHLCV
مصدر البيانات: yfinance (XAUUSD=X — Gold Spot)
الترقية المستقبلية: استبدل fetch_gold_ohlcv بـ WebSocket tick provider
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from ..core.database import Candle, Session, init_db
from ..core.config import settings


def fetch_gold_ohlcv(period: str = None, interval: str = "1h") -> pd.DataFrame:
    """جلب OHLCV من yfinance وتنظيفه"""
    period = period or settings.HISTORY_PERIOD
    raw = yf.download(settings.SYMBOL, period=period, interval=interval, progress=False)

    # yfinance قد يرجع tuple في بعض الإصدارات
    if isinstance(raw, tuple):
        raw = raw[0]

    if not isinstance(raw, pd.DataFrame) or raw.empty:
        raise ValueError(f"yfinance لم يرجع بيانات: {settings.SYMBOL}")

    # تسوية أسماء الأعمدة (MultiIndex → flat)
    raw.columns = [
        c[0].lower() if isinstance(c, tuple) else c.lower()
        for c in raw.columns
    ]
    raw = raw.dropna(subset=["open", "high", "low", "close"])
    return raw


def store_candles(df: pd.DataFrame) -> int:
    """تخزين الشموع في DB — يتجاهل المكررات (upsert بسيط)"""
    session = Session()
    count   = 0
    try:
        for ts, row in df.iterrows():
            ts_dt = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            # remove timezone for SQLite compatibility
            ts_dt = ts_dt.replace(tzinfo=None)

            if session.query(Candle).filter(Candle.ts == ts_dt).count():
                continue

            session.add(Candle(
                ts     = ts_dt,
                open   = float(row["open"]),
                high   = float(row["high"]),
                low    = float(row["low"]),
                close  = float(row["close"]),
                volume = float(row.get("volume", 0) or 0),
            ))
            count += 1

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return count


def update_data() -> dict:
    """تحديث كامل: جلب + تخزين"""
    init_db()
    df     = fetch_gold_ohlcv()
    stored = store_candles(df)
    return {
        "fetched":     len(df),
        "stored_new":  stored,
        "ts":          datetime.utcnow().isoformat(),
    }


def load_candles_df() -> pd.DataFrame:
    """تحميل الشموع من DB كـ DataFrame مرتّب زمنياً"""
    session = Session()
    try:
        rows = session.query(Candle).order_by(Candle.ts).all()
        if not rows:
            return pd.DataFrame()
        data = [
            {"ts": r.ts, "open": r.open, "high": r.high,
             "low": r.low, "close": r.close, "volume": r.volume}
            for r in rows
        ]
        return pd.DataFrame(data).set_index("ts")
    finally:
        session.close()
