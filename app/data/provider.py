"""
Unified OHLCV Data Provider for XAUUSD
Priority:
  1. Twelve Data API  — if TWELVEDATA_KEY env var is set
     Free tier: 800 credits/day  |  Sign up: twelvedata.com (no credit card)
  2. yfinance GC=F    — fallback (Gold Futures, reliable OHLCV, ~$5-10 premium)
"""
import os
import time
import pandas as pd
import numpy as np

TWELVEDATA_KEY = os.getenv("TWELVEDATA_KEY", "")

# Twelve Data interval names
_TD_INTERVAL = {
    "1m":  "1min",
    "5m":  "5min",
    "15m": "15min",
    "30m": "30min",
    "1h":  "1h",
    "4h":  "4h",
    "1d":  "1day",
    "1w":  "1week",
    "1mo": "1month",
    # multi_tf_analysis keys
    "monthly": "1month",
    "weekly":  "1week",
    "daily":   "1day",
    "h4":      "4h",
    "h1":      "1h",
    "m15":     "15min",
    "m5":      "5min",
}

# yfinance interval + period for each TF key
_YF_PARAMS = {
    "1m":     ("1m",   "5d"),
    "5m":     ("5m",   "7d"),
    "15m":    ("15m",  "20d"),
    "30m":    ("30m",  "30d"),
    "1h":     ("1h",   "60d"),
    "4h":     ("1h",   "60d"),   # resample 1h→4h
    "1d":     ("1d",   "2y"),
    "1w":     ("1wk",  "5y"),
    "1mo":    ("1mo",  "10y"),
    # multi_tf_analysis keys
    "monthly": ("1mo", "10y"),
    "weekly":  ("1wk", "5y"),
    "daily":   ("1d",  "2y"),
    "h4":      ("1h",  "60d"),   # resample
    "h1":      ("1h",  "60d"),
    "m15":     ("15m", "20d"),
    "m5":      ("5m",  "7d"),
}

# Number of candles to request per TF for Twelve Data
_TD_OUTPUTSIZE = {
    "monthly": 60, "weekly": 104, "daily": 365,
    "h4": 300, "h1": 300, "m15": 300, "m5": 300,
    "1mo": 60, "1w": 104, "1d": 365,
    "4h": 300, "1h": 300, "15m": 300, "5m": 300, "1m": 300,
}

# Simple in-memory cache {key: (df, ts)}
_cache: dict = {}
_CACHE_TTL = {
    "monthly": 3600, "weekly": 3600, "daily": 900,
    "h4": 600, "h1": 300, "m15": 120, "m5": 60,
    "1mo": 3600, "1w": 3600, "1d": 900,
    "4h": 600, "1h": 300, "15m": 120, "5m": 60, "1m": 30,
}


def _flatten_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten yfinance MultiIndex columns to simple lowercase strings."""
    df.columns = [
        c[0].lower() if isinstance(c, tuple) else str(c).lower()
        for c in df.columns
    ]
    return df


def _validate(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only OHLCV columns, drop bad rows, ensure numeric."""
    needed = ["open", "high", "low", "close"]
    for col in needed:
        if col not in df.columns:
            return pd.DataFrame()
    df = df[needed + (["volume"] if "volume" in df.columns else [])].copy()
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=needed)
    # Sanity check: gold should be roughly 1500–5000
    df = df[(df["close"] > 1000) & (df["close"] < 10000)]
    return df


# ── Twelve Data ───────────────────────────────────────────────────────────────

def _fetch_twelvedata(tf: str, outputsize: int = 300) -> pd.DataFrame:
    import httpx
    interval = _TD_INTERVAL.get(tf, "1h")
    resp = httpx.get(
        "https://api.twelvedata.com/time_series",
        params={
            "symbol":     "XAU/USD",
            "interval":   interval,
            "outputsize": outputsize,
            "apikey":     TWELVEDATA_KEY,
            "format":     "JSON",
            "order":      "ASC",
        },
        timeout=15,
    )
    data = resp.json()
    if data.get("status") == "error":
        raise ValueError(f"TwelveData: {data.get('message')}")
    values = data.get("values", [])
    if not values:
        raise ValueError("TwelveData: empty response")

    rows = [{
        "open":   float(v["open"]),
        "high":   float(v["high"]),
        "low":    float(v["low"]),
        "close":  float(v["close"]),
        "volume": float(v.get("volume") or 0),
    } for v in values]

    df = pd.DataFrame(rows)
    # Parse datetime index
    times = [v["datetime"] for v in values]
    df.index = pd.to_datetime(times)
    return df


# ── yfinance ─────────────────────────────────────────────────────────────────

def _fetch_yfinance(tf: str) -> pd.DataFrame:
    import yfinance as yf
    interval, period = _YF_PARAMS.get(tf, ("1h", "60d"))
    raw = yf.download("GC=F", period=period, interval=interval,
                      progress=False, auto_adjust=True)
    if isinstance(raw, tuple):
        raw = raw[0]
    if raw.empty:
        return pd.DataFrame()
    df = _flatten_cols(raw)

    # Resample 1h → 4h  (yfinance has no native 4h)
    if tf in ("4h", "h4"):
        df.index = pd.to_datetime(df.index)
        agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
        if "volume" in df.columns:
            agg["volume"] = "sum"
        df = df.resample("4h").agg(agg).dropna(subset=["open", "close"])

    return df


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_ohlcv(tf: str, limit: int = 300, use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch XAUUSD OHLCV.
    Returns clean DataFrame with columns: open, high, low, close[, volume]
    DatetimeIndex, sorted ascending.
    """
    now = time.time()
    ttl = _CACHE_TTL.get(tf, 300)
    cache_key = tf

    if use_cache and cache_key in _cache:
        df_c, ts = _cache[cache_key]
        if now - ts < ttl:
            return df_c.tail(limit)

    df = pd.DataFrame()

    # 1. Try Twelve Data
    if TWELVEDATA_KEY:
        try:
            df = _fetch_twelvedata(tf, min(limit + 20, 5000))
        except Exception:
            df = pd.DataFrame()

    # 2. Fallback: yfinance
    if df.empty:
        try:
            df = _fetch_yfinance(tf)
        except Exception:
            return pd.DataFrame()

    df = _validate(df)
    if df.empty:
        return df

    df = df.sort_index().tail(limit)
    _cache[cache_key] = (df, now)
    return df


def get_live_price() -> float:
    """Fast spot price — Twelve Data if available, else yfinance fast_info."""
    if TWELVEDATA_KEY:
        try:
            import httpx
            r = httpx.get(
                "https://api.twelvedata.com/price",
                params={"symbol": "XAU/USD", "apikey": TWELVEDATA_KEY},
                timeout=5,
            )
            return float(r.json()["price"])
        except Exception:
            pass
    try:
        import yfinance as yf
        fi = yf.Ticker("XAUUSD=X").fast_info
        p = float(fi.last_price or 0)
        if p > 1000:
            return p
    except Exception:
        pass
    return 0.0
