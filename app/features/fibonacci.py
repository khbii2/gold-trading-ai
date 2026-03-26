"""
Fibonacci Retracement + Order Block + Golden Zone Engine
استراتيجية: رسم فيبوناتشي من القاع للقمة (أو العكس) على فريم 15M
بعد تحديد الاتجاه + مناطق الدعم/المقاومة + تأكيد سحب السيولة
دخول في Golden Zone (0.618–0.786) مع تقاطع Order Block
"""
import pandas as pd
import numpy as np

# ── Fibonacci Levels ──────────────────────────────────────────────────────────
FIB_LEVELS = {
    "0.0":   0.0,
    "0.236": 0.236,
    "0.382": 0.382,
    "0.5":   0.5,
    "0.618": 0.618,
    "0.705": 0.705,
    "0.786": 0.786,
    "1.0":   1.0,
    "1.272": 1.272,  # extension
    "1.618": 1.618,  # extension
}

GOLDEN_ZONE_LOW  = 0.618
GOLDEN_ZONE_HIGH = 0.786


# ── Swing Detection ───────────────────────────────────────────────────────────

def _detect_swings(df: pd.DataFrame, lookback: int = 5) -> list:
    """
    ZigZag-style swing detection.
    Returns list of (idx, price, 'high'|'low')
    A swing high: highest point in window [i-lb .. i+lb]
    A swing low:  lowest  point in window [i-lb .. i+lb]
    """
    h = df["high"].values
    l = df["low"].values
    n = len(df)
    swings = []

    for i in range(lookback, n - lookback):
        window_h = h[i - lookback: i + lookback + 1]
        window_l = l[i - lookback: i + lookback + 1]
        if h[i] >= window_h.max():
            swings.append((i, float(h[i]), "high"))
        elif l[i] <= window_l.min():
            swings.append((i, float(l[i]), "low"))

    return swings


def _last_significant_swing(df: pd.DataFrame, lookback: int = 5):
    """
    Returns the most recent pair (swing_high_info, swing_low_info)
    that form a significant move worth drawing Fibonacci on.
    """
    swings = _detect_swings(df, lookback)
    if len(swings) < 2:
        return None, None

    last_high = next((s for s in reversed(swings) if s[2] == "high"), None)
    last_low  = next((s for s in reversed(swings) if s[2] == "low"),  None)
    return last_high, last_low


# ── Fibonacci Levels Calculator ───────────────────────────────────────────────

def calc_fib_levels(swing_low: float, swing_high: float, direction: str) -> dict:
    """
    direction='up'   → uptrend move, retracement goes DOWN from high to low
    direction='down' → downtrend move, retracement goes UP from low to high
    Returns {label: price}
    """
    diff = swing_high - swing_low
    result = {}
    for label, ratio in FIB_LEVELS.items():
        if direction == "up":
            result[label] = round(swing_high - diff * ratio, 2)
        else:
            result[label] = round(swing_low  + diff * ratio, 2)
    return result


# ── Order Block Detection ─────────────────────────────────────────────────────

def detect_order_blocks(df: pd.DataFrame, confirm_candles: int = 2) -> list:
    """
    Detect Order Blocks:
    - Bullish OB: last bearish candle BEFORE a strong bullish impulse
    - Bearish OB: last bullish candle BEFORE a strong bearish impulse

    Returns list of dicts sorted by recency (newest last)
    """
    c = df["close"].values
    o = df["open"].values
    h = df["high"].values
    l = df["low"].values
    n = len(df)
    obs = []

    for i in range(1, n - confirm_candles - 1):
        body_i = abs(c[i] - o[i])
        if body_i < 1e-8:
            continue  # ignore doji for OB base

        # Bullish OB: bearish candle → followed by bullish impulse
        if c[i] < o[i]:
            next_bulls = sum(1 for j in range(i + 1, min(i + 1 + confirm_candles, n))
                             if c[j] > o[j])
            # Check impulse size: next close breaks above OB high
            if next_bulls >= confirm_candles and c[min(i + confirm_candles, n - 1)] > h[i]:
                obs.append({
                    "type":   "bullish",
                    "top":    round(float(h[i]), 2),
                    "bottom": round(float(l[i]), 2),
                    "mid":    round((float(h[i]) + float(l[i])) / 2, 2),
                    "idx":    i,
                })

        # Bearish OB: bullish candle → followed by bearish impulse
        elif c[i] > o[i]:
            next_bears = sum(1 for j in range(i + 1, min(i + 1 + confirm_candles, n))
                             if c[j] < o[j])
            if next_bears >= confirm_candles and c[min(i + confirm_candles, n - 1)] < l[i]:
                obs.append({
                    "type":   "bearish",
                    "top":    round(float(h[i]), 2),
                    "bottom": round(float(l[i]), 2),
                    "mid":    round((float(h[i]) + float(l[i])) / 2, 2),
                    "idx":    i,
                })

    return obs[-8:]  # keep last 8


# ── Liquidity Sweep Detector ──────────────────────────────────────────────────

def _check_sweep(df: pd.DataFrame, swing_low: float, swing_high: float,
                 direction: str, lookback: int = 20) -> bool:
    """
    Checks if price swept (wicked through) the swing point before entering
    the Golden Zone — the key liquidity confirmation.
    """
    recent = df.tail(lookback)
    if direction == "up":
        # Bullish: price should have swept below swing_low (grabbed sell stops)
        # then reversed back up
        swept = (recent["low"] < swing_low * 1.0005).any()
        bounced = float(df["close"].iloc[-1]) > swing_low
        return bool(swept and bounced)
    else:
        # Bearish: price swept above swing_high then reversed down
        swept = (recent["high"] > swing_high * 0.9995).any()
        bounced = float(df["close"].iloc[-1]) < swing_high
        return bool(swept and bounced)


# ── Main Analysis ─────────────────────────────────────────────────────────────

def golden_zone_analysis(df: pd.DataFrame, lookback: int = 5) -> dict:
    """
    Full Fibonacci + Golden Zone + Order Block analysis.

    Entry conditions (scored 0–100):
      40 pts — price inside Golden Zone (0.618–0.786)
      25 pts — Order Block inside / overlapping Golden Zone
      20 pts — Liquidity sweep confirmed before zone entry
      15 pts — Confirmation candle CLOSED inside zone (not just wick)

    entry_signal fires when score ≥ 70
    """
    empty = {
        "swing_high":      None,
        "swing_low":       None,
        "direction":       None,
        "fib_levels":      {},
        "golden_zone":     None,
        "in_golden_zone":  False,
        "order_blocks":    [],
        "ob_in_golden_zone": False,
        "sweep_confirmed": False,
        "entry_quality":   0,
        "entry_signal":    None,
        "conditions":      [],
    }

    if df is None or len(df) < 20:
        return empty

    last_high, last_low = _last_significant_swing(df, lookback)
    if not last_high or not last_low:
        return empty

    # Determine direction from which swing came last
    if last_high[0] > last_low[0]:
        direction     = "up"       # last move was up → retracement expected down
        swing_low_p   = last_low[1]
        swing_high_p  = last_high[1]
    else:
        direction     = "down"     # last move was down → retracement expected up
        swing_low_p   = last_low[1]
        swing_high_p  = last_high[1]

    fib = calc_fib_levels(swing_low_p, swing_high_p, direction)

    # Golden Zone boundaries
    gz618 = fib["0.618"]
    gz786 = fib["0.786"]
    gz_top    = max(gz618, gz786)
    gz_bottom = min(gz618, gz786)

    current_price = float(df["close"].iloc[-1])
    last_open     = float(df["open"].iloc[-1])

    # ── Scoring ──────────────────────────────────────────────────────────────
    score = 0
    conditions = []

    # 1. Price inside Golden Zone
    in_gz = gz_bottom <= current_price <= gz_top
    if in_gz:
        score += 40
        conditions.append({"met": True,  "detail": f"Price in Golden Zone ({gz_bottom}–{gz_top})", "weight": 40})
    else:
        conditions.append({"met": False, "detail": f"Price NOT in Golden Zone ({gz_bottom}–{gz_top})", "weight": 40})

    # 2. Order Block in Golden Zone
    obs = detect_order_blocks(df)
    target_ob_type = "bullish" if direction == "up" else "bearish"
    ob_in_gz = any(
        (gz_bottom <= ob["top"] <= gz_top * 1.002) or (gz_bottom * 0.998 <= ob["bottom"] <= gz_top)
        for ob in obs if ob["type"] == target_ob_type
    )
    if ob_in_gz:
        score += 25
        conditions.append({"met": True,  "detail": f"{target_ob_type.capitalize()} OB inside Golden Zone", "weight": 25})
    else:
        conditions.append({"met": False, "detail": f"No {target_ob_type} OB in Golden Zone", "weight": 25})

    # 3. Liquidity sweep before zone entry
    sweep = _check_sweep(df, swing_low_p, swing_high_p, direction)
    if sweep:
        score += 20
        conditions.append({"met": True,  "detail": "Liquidity sweep confirmed before zone", "weight": 20})
    else:
        conditions.append({"met": False, "detail": "No liquidity sweep detected", "weight": 20})

    # 4. Confirmation candle closed inside zone
    candle_closed_in_gz = gz_bottom <= current_price <= gz_top and \
                          gz_bottom <= last_open <= gz_top * 1.002
    if candle_closed_in_gz:
        score += 15
        conditions.append({"met": True,  "detail": "Entry candle closed inside Golden Zone", "weight": 15})
    else:
        conditions.append({"met": False, "detail": "No candle close confirmation in zone", "weight": 15})

    entry_signal = None
    if score >= 70:
        entry_signal = "buy" if direction == "up" else "sell"

    return {
        "swing_high":      round(swing_high_p, 2),
        "swing_low":       round(swing_low_p,  2),
        "direction":       direction,
        "fib_levels":      fib,
        "golden_zone":     {"top": round(gz_top, 2), "bottom": round(gz_bottom, 2)},
        "in_golden_zone":  in_gz,
        "order_blocks":    [
            {"type": ob["type"], "top": ob["top"], "bottom": ob["bottom"], "mid": ob["mid"]}
            for ob in obs[-5:]
        ],
        "ob_in_golden_zone": ob_in_gz,
        "sweep_confirmed": sweep,
        "entry_quality":   score,
        "entry_signal":    entry_signal,
        "conditions":      conditions,
    }
