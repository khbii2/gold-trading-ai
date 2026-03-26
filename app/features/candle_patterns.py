"""
Candlestick Pattern Detection
Hammer, Pin Bar, Engulfing, Shooting Star, Doji, Morning/Evening Star
"""
import pandas as pd
import numpy as np


def _parts(o, h, l, c):
    body      = abs(c - o)
    full      = h - l + 1e-9
    upper     = h - max(o, c)
    lower     = min(o, c) - l
    body_pct  = body / full
    upper_pct = upper / full
    lower_pct = lower / full
    bullish   = c > o
    return body, full, upper, lower, body_pct, upper_pct, lower_pct, bullish


def is_hammer(o, h, l, c) -> bool:
    """Hammer / Bullish Pin Bar — long lower wick, small body at top"""
    body, full, upper, lower, bp, up, lp, bull = _parts(o, h, l, c)
    return lp >= 0.55 and bp <= 0.35 and up <= 0.15


def is_shooting_star(o, h, l, c) -> bool:
    """Shooting Star / Bearish Pin Bar — long upper wick, small body at bottom"""
    body, full, upper, lower, bp, up, lp, bull = _parts(o, h, l, c)
    return up >= 0.55 and bp <= 0.35 and lp <= 0.15


def is_doji(o, h, l, c) -> bool:
    """Doji — very small body, wicks on both sides"""
    body, full, upper, lower, bp, up, lp, bull = _parts(o, h, l, c)
    return bp <= 0.10


def is_bullish_engulfing(o1, h1, l1, c1, o2, h2, l2, c2) -> bool:
    """Bullish Engulfing — candle2 (bull) fully engulfs candle1 (bear)"""
    prev_bear = c1 < o1
    curr_bull = c2 > o2
    engulfs   = o2 <= c1 and c2 >= o1
    return prev_bear and curr_bull and engulfs


def is_bearish_engulfing(o1, h1, l1, c1, o2, h2, l2, c2) -> bool:
    """Bearish Engulfing — candle2 (bear) fully engulfs candle1 (bull)"""
    prev_bull = c1 > o1
    curr_bear = c2 < o2
    engulfs   = o2 >= c1 and c2 <= o1
    return prev_bull and curr_bear and engulfs


def detect_patterns(df: pd.DataFrame) -> list:
    """
    Scan last 3 candles and return detected patterns
    Returns list of dicts: {pattern, direction, strength}
    """
    if len(df) < 3:
        return []

    patterns = []
    # Last candle
    c  = df.iloc[-1]
    c1 = df.iloc[-2]

    o, h, l, close = float(c["open"]), float(c["high"]), float(c["low"]), float(c["close"])
    o1,h1,l1,c1v   = float(c1["open"]),float(c1["high"]),float(c1["low"]),float(c1["close"])

    if is_hammer(o, h, l, close):
        patterns.append({"pattern": "Hammer", "direction": "bullish", "strength": 75})

    if is_shooting_star(o, h, l, close):
        patterns.append({"pattern": "Shooting Star", "direction": "bearish", "strength": 75})

    if is_doji(o, h, l, close):
        patterns.append({"pattern": "Doji", "direction": "neutral", "strength": 50})

    if is_bullish_engulfing(o1, h1, l1, c1v, o, h, l, close):
        patterns.append({"pattern": "Bullish Engulfing", "direction": "bullish", "strength": 85})

    if is_bearish_engulfing(o1, h1, l1, c1v, o, h, l, close):
        patterns.append({"pattern": "Bearish Engulfing", "direction": "bearish", "strength": 85})

    # Marubozu — full body candle (strong momentum)
    body, full, *_ = _parts(o, h, l, close)
    if body / full >= 0.80:
        direction = "bullish" if close > o else "bearish"
        patterns.append({"pattern": "Marubozu", "direction": direction, "strength": 80})

    return patterns
