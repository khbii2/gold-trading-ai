"""
Technical Indicators — EMAs, RSI, MACD, ATR
"""
import pandas as pd
import numpy as np


def ema(s: pd.Series, period: int) -> pd.Series:
    return s.ewm(span=period, adjust=False).mean()


def rsi(s: pd.Series, period: int = 14) -> pd.Series:
    d = s.diff()
    g = d.clip(lower=0).rolling(period).mean()
    l = (-d.clip(upper=0)).rolling(period).mean()
    rs = g / l.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(s: pd.Series, fast=12, slow=26, signal=9) -> dict:
    e_fast   = ema(s, fast)
    e_slow   = ema(s, slow)
    line     = e_fast - e_slow
    sig_line = ema(line, signal)
    hist     = line - sig_line
    return {"line": line, "signal": sig_line, "hist": hist}


def atr(h: pd.Series, l: pd.Series, c: pd.Series, period=14) -> pd.Series:
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()
