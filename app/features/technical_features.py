"""
Technical Feature Engineering — Phase 3
Features من OHLCV للنموذج الأول

المرحلة 4 ستضيف: orderflow_features.py
المرحلة 6 ستضيف: smc_features.py, news_features.py
"""
import pandas as pd
import numpy as np


# ── Indicators ─────────────────────────────────────────────────────────────

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low  - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


# ── Feature columns expected by the model ──────────────────────────────────

FEATURE_COLS = [
    "ret_1h",
    "ret_4h",
    "ret_24h",
    "ma20_ratio",
    "ma50_ratio",
    "ma200_ratio",
    "rsi_14",
    "atr_norm",
    "bb_width",
    "vol_ratio",
    "hour",
    "dow",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    بناء feature matrix من OHLCV DataFrame
    Returns: DataFrame يشمل FEATURE_COLS + 'label' (اتجاه الشمعة القادمة)
    """
    c = df["close"]
    h = df["high"]
    l = df["low"]

    f = pd.DataFrame(index=df.index)

    # ── Returns ────────────────────────────────────────────────────────────
    f["ret_1h"]  = c.pct_change(1)
    f["ret_4h"]  = c.pct_change(4)
    f["ret_24h"] = c.pct_change(24)

    # ── Moving Average ratios ───────────────────────────────────────────────
    f["ma20_ratio"]  = c.rolling(20).mean()  / c
    f["ma50_ratio"]  = c.rolling(50).mean()  / c
    f["ma200_ratio"] = c.rolling(200).mean() / c

    # ── RSI (normalized 0–1) ────────────────────────────────────────────────
    f["rsi_14"] = _rsi(c, 14) / 100.0

    # ── ATR normalized ─────────────────────────────────────────────────────
    f["atr_norm"] = _atr(h, l, c, 14) / c

    # ── Bollinger Band width ────────────────────────────────────────────────
    ma20  = c.rolling(20).mean()
    std20 = c.rolling(20).std()
    f["bb_width"] = (2 * std20) / ma20.replace(0, np.nan)

    # ── Volume ratio ────────────────────────────────────────────────────────
    if "volume" in df.columns and df["volume"].sum() > 0:
        vol_ma       = df["volume"].rolling(20).mean()
        f["vol_ratio"] = df["volume"] / vol_ma.replace(0, np.nan)
    else:
        f["vol_ratio"] = 1.0

    # ── Time features (normalized) ──────────────────────────────────────────
    idx = df.index
    if hasattr(idx, "hour"):
        f["hour"] = idx.hour  / 23.0
        f["dow"]  = idx.dayofweek / 6.0
    else:
        f["hour"] = 0.5
        f["dow"]  = 0.5

    # ── Label: شمعة قادمة صاعدة = 1، هابطة = 0 ────────────────────────────
    f["label"] = (c.shift(-1) > c).astype(int)

    return f.dropna()
