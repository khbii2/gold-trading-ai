"""
Multi-Timeframe Analysis Engine
Monthly → Weekly → Daily → H4 → H1 → 15M → 5M

يحلل كل فريم ويعطي:
- اتجاه EMA
- بنية السوق (HH/HL أو LH/LL)
- مستويات الدعم والمقاومة
- مناطق السيولة
- شموع انعكاسية
- إشارة دخول مشروطة
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from .indicators import ema, rsi, macd, atr
from .candle_patterns import detect_patterns

SYMBOL = "XAUUSD=X"

# الفريمات المطلوبة
TIMEFRAMES = {
    "monthly": ("1mo", "5y"),
    "weekly":  ("1wk", "2y"),
    "daily":   ("1d",  "1y"),
    "h4":      ("4h",  "60d"),
    "h1":      ("1h",  "30d"),
    "m15":     ("15m", "20d"),
    "m5":      ("5m",  "7d"),
}


def _fetch(interval: str, period: str) -> pd.DataFrame:
    df = yf.download(SYMBOL, period=period, interval=interval,
                     progress=False, auto_adjust=True)
    if isinstance(df, tuple): df = df[0]
    if df.empty: return pd.DataFrame()
    df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]
    return df.dropna()


def _ema_trend(df: pd.DataFrame) -> dict:
    """اتجاه EMA — يعيد trend + قيم EMAs"""
    c = df["close"]
    e9   = ema(c, 9).iloc[-1]
    e20  = ema(c, 20).iloc[-1]
    e50  = ema(c, 50).iloc[-1]
    e200 = ema(c, 200).iloc[-1] if len(c) >= 200 else None
    price = float(c.iloc[-1])

    # الاتجاه بناءً على ترتيب EMAs
    if price > e20 > e50 and (e200 is None or e50 > e200):
        trend = "bullish"
    elif price < e20 < e50 and (e200 is None or e50 < e200):
        trend = "bearish"
    else:
        trend = "neutral"

    return {
        "trend":  trend,
        "ema9":   round(e9,   2),
        "ema20":  round(e20,  2),
        "ema50":  round(e50,  2),
        "ema200": round(e200, 2) if e200 else None,
        "price":  round(price, 2),
    }


def _market_structure(df: pd.DataFrame) -> str:
    """تحديد بنية السوق — HH/HL أو LH/LL أو ranging"""
    if len(df) < 10:
        return "unknown"
    # أخذ آخر 20 شمعة وإيجاد Swing H/L
    highs = df["high"].tail(20).values
    lows  = df["low"].tail(20).values

    # مقارنة آخر قمة وقاع بالسابقتين
    h_now, h_prev = highs[-1], highs[-6]
    l_now, l_prev = lows[-1],  lows[-6]

    hh = h_now > h_prev
    hl = l_now > l_prev
    lh = h_now < h_prev
    ll = l_now < l_prev

    if hh and hl: return "uptrend"
    if lh and ll: return "downtrend"
    return "ranging"


def _support_resistance(df: pd.DataFrame, n=5) -> dict:
    """إيجاد مستويات الدعم والمقاومة الرئيسية"""
    h = df["high"].values
    l = df["low"].values
    c = df["close"].values
    size = len(df)
    pivots_h, pivots_l = [], []

    for i in range(n, size - n):
        if all(h[i] >= h[i-j] for j in range(1, n+1)) and all(h[i] >= h[i+j] for j in range(1, n+1)):
            pivots_h.append(float(h[i]))
        if all(l[i] <= l[i-j] for j in range(1, n+1)) and all(l[i] <= l[i+j] for j in range(1, n+1)):
            pivots_l.append(float(l[i]))

    price = float(c[-1])
    # أقرب 3 مقاومات فوق السعر + 3 دعوم تحته
    res  = sorted([v for v in set(pivots_h) if v > price])[:3]
    sup  = sorted([v for v in set(pivots_l) if v < price], reverse=True)[:3]
    return {"resistances": [round(v, 2) for v in res],
            "supports":    [round(v, 2) for v in sup]}


def _liquidity_levels(df: pd.DataFrame) -> dict:
    """
    مناطق السيولة:
    - Buy-side: أعلى القمم (Stop Losses المشترين الشورت)
    - Sell-side: أدنى القيعان (Stop Losses البائعين اللونق)
    - Equal Highs/Lows: تجمعات السيولة
    - Last Sweep: آخر سحب سيولة
    """
    h = df["high"].tail(50).values
    l = df["low"].tail(50).values
    c = df["close"].tail(50).values
    price = float(c[-1])

    # Buy-side liquidity = أعلى القمم الأخيرة
    buy_side  = sorted(set([round(float(v), 2) for v in h if v > price]), reverse=True)[:4]
    # Sell-side liquidity = أدنى القيعان الأخيرة
    sell_side = sorted(set([round(float(v), 2) for v in l if v < price]))[:4]

    # Equal Highs — قمم متقاربة جداً (سيولة مكدّسة)
    equal_highs = []
    for i in range(len(h)-1):
        if abs(h[i] - h[i+1]) / h[i] < 0.001:   # 0.1% tolerance
            equal_highs.append(round(float(max(h[i], h[i+1])), 2))

    equal_lows = []
    for i in range(len(l)-1):
        if abs(l[i] - l[i+1]) / l[i] < 0.001:
            equal_lows.append(round(float(min(l[i], l[i+1])), 2))

    # Sweep detection — آخر كسر لقمة/قاع مع إغلاق عكسي
    sweep = None
    for i in range(5, min(20, len(df))):
        prev_high = float(df["high"].iloc[-(i+1)])
        curr_high = float(df["high"].iloc[-i])
        curr_close = float(df["close"].iloc[-i])
        if curr_high > prev_high and curr_close < prev_high:
            sweep = {"direction": "bearish", "level": round(prev_high, 2),
                     "type": "Buy-Side Sweep"}
            break
        prev_low  = float(df["low"].iloc[-(i+1)])
        curr_low  = float(df["low"].iloc[-i])
        curr_close2 = float(df["close"].iloc[-i])
        if curr_low < prev_low and curr_close2 > prev_low:
            sweep = {"direction": "bullish", "level": round(prev_low, 2),
                     "type": "Sell-Side Sweep"}
            break

    return {
        "buy_side":    buy_side,
        "sell_side":   sell_side,
        "equal_highs": list(set(equal_highs))[:3],
        "equal_lows":  list(set(equal_lows))[:3],
        "last_sweep":  sweep,
    }


def _analyze_tf(df: pd.DataFrame, tf_name: str) -> dict:
    """تحليل فريم واحد كامل"""
    if df.empty or len(df) < 20:
        return {"error": "insufficient_data"}

    c = df["close"]
    price = float(c.iloc[-1])

    ema_data   = _ema_trend(df)
    structure  = _market_structure(df)
    sr         = _support_resistance(df)
    rsi_val    = float(rsi(c, 14).iloc[-1])
    macd_data  = macd(c)
    macd_hist  = float(macd_data["hist"].iloc[-1])
    patterns   = detect_patterns(df.tail(5))
    atr_val    = float(atr(df["high"], df["low"], c, 14).iloc[-1])

    return {
        "timeframe":  tf_name,
        "price":      round(price, 2),
        "trend":      ema_data["trend"],
        "structure":  structure,
        "ema":        ema_data,
        "rsi":        round(rsi_val, 1),
        "macd_hist":  round(macd_hist, 3),
        "atr":        round(atr_val, 2),
        "patterns":   patterns,
        "sr":         sr,
    }


def _entry_signal(analyses: dict, liq: dict) -> dict:
    """
    إشارة الدخول المشروطة
    الشروط مرتّبة من الأكبر للأصغر
    """
    conditions_met     = []
    conditions_missing = []

    tf_monthly = analyses.get("monthly", {})
    tf_weekly  = analyses.get("weekly",  {})
    tf_daily   = analyses.get("daily",   {})
    tf_h4      = analyses.get("h4",      {})
    tf_h1      = analyses.get("h1",      {})
    tf_m15     = analyses.get("m15",     {})
    tf_m5      = analyses.get("m5",      {})

    price = tf_h1.get("price", 0) or tf_daily.get("price", 0)

    # ── 1. اتجاه الفريم الكبير ────────────────────────────────────────────
    big_trends = [
        tf_monthly.get("trend", "neutral"),
        tf_weekly.get("trend",  "neutral"),
        tf_daily.get("trend",   "neutral"),
    ]
    bull_big = big_trends.count("bullish")
    bear_big = big_trends.count("bearish")

    if bull_big >= 2:
        conditions_met.append({"cond": "big_tf_trend", "detail": "Monthly/Weekly/Daily → Bullish", "weight": 25})
        macro = "buy"
    elif bear_big >= 2:
        conditions_met.append({"cond": "big_tf_trend", "detail": "Monthly/Weekly/Daily → Bearish", "weight": 25})
        macro = "sell"
    else:
        conditions_missing.append({"cond": "big_tf_trend", "detail": "فريمات الكبيرة غير متوافقة", "weight": 25})
        macro = "neutral"

    # ── 2. H4 + H1 تأكيد ─────────────────────────────────────────────────
    h4_trend = tf_h4.get("trend", "neutral")
    h1_trend = tf_h1.get("trend", "neutral")

    if macro == "buy" and h1_trend in ("bullish", "neutral"):
        conditions_met.append({"cond": "h1_confirm", "detail": f"H1 trend = {h1_trend}", "weight": 20})
    elif macro == "sell" and h1_trend in ("bearish", "neutral"):
        conditions_met.append({"cond": "h1_confirm", "detail": f"H1 trend = {h1_trend}", "weight": 20})
    else:
        conditions_missing.append({"cond": "h1_confirm", "detail": f"H1 عكس الاتجاه العام ({h1_trend})", "weight": 20})

    # ── 3. عند منطقة دعم/مقاومة ─────────────────────────────────────────
    h1_sr = tf_h1.get("sr", {})
    sup = h1_sr.get("supports", [price * 0.99])
    res = h1_sr.get("resistances", [price * 1.01])
    near_sup = sup and abs(price - sup[0]) / price < 0.003    # 0.3%
    near_res = res and abs(price - res[0]) / price < 0.003

    if macro == "buy" and near_sup:
        conditions_met.append({"cond": "at_level", "detail": f"عند دعم ${sup[0]}", "weight": 20})
    elif macro == "sell" and near_res:
        conditions_met.append({"cond": "at_level", "detail": f"عند مقاومة ${res[0]}", "weight": 20})
    else:
        # تحقق من السيولة
        sell_side = liq.get("sell_side", [])
        buy_side  = liq.get("buy_side", [])
        if macro == "buy" and sell_side and abs(price - sell_side[0]) / price < 0.005:
            conditions_met.append({"cond": "at_level", "detail": f"عند سيولة ${sell_side[0]}", "weight": 15})
        elif macro == "sell" and buy_side and abs(price - buy_side[0]) / price < 0.005:
            conditions_met.append({"cond": "at_level", "detail": f"عند سيولة ${buy_side[0]}", "weight": 15})
        else:
            conditions_missing.append({"cond": "at_level", "detail": "السعر ليس عند منطقة دعم/مقاومة/سيولة", "weight": 20})

    # ── 4. شمعة انعكاسية على 5M / 15M ──────────────────────────────────
    entry_patterns = tf_m5.get("patterns", []) + tf_m15.get("patterns", [])
    bull_patterns  = [p for p in entry_patterns if p["direction"] == "bullish"]
    bear_patterns  = [p for p in entry_patterns if p["direction"] == "bearish"]

    if macro == "buy" and bull_patterns:
        p = bull_patterns[0]
        conditions_met.append({"cond": "pattern", "detail": f"{p['pattern']} على 5M/15M", "weight": 20})
    elif macro == "sell" and bear_patterns:
        p = bear_patterns[0]
        conditions_met.append({"cond": "pattern", "detail": f"{p['pattern']} على 5M/15M", "weight": 20})
    else:
        conditions_missing.append({"cond": "pattern", "detail": "لا شمعة انعكاسية على 5M/15M", "weight": 20})

    # ── 5. RSI ────────────────────────────────────────────────────────────
    rsi_h1  = tf_h1.get("rsi", 50)
    rsi_m15 = tf_m15.get("rsi", 50)

    if macro == "buy" and rsi_h1 < 65 and rsi_m15 < 70:
        conditions_met.append({"cond": "rsi", "detail": f"RSI H1={rsi_h1:.0f} / 15M={rsi_m15:.0f} — مساحة للصعود", "weight": 10})
    elif macro == "sell" and rsi_h1 > 35 and rsi_m15 > 30:
        conditions_met.append({"cond": "rsi", "detail": f"RSI H1={rsi_h1:.0f} / 15M={rsi_m15:.0f} — مساحة للهبوط", "weight": 10})
    else:
        conditions_missing.append({"cond": "rsi", "detail": f"RSI H1={rsi_h1:.0f} / 15M={rsi_m15:.0f} — منطقة ممتدة", "weight": 10})

    # ── 6. Sweep تأكيد ───────────────────────────────────────────────────
    sweep = liq.get("last_sweep")
    if sweep:
        if macro == "buy" and sweep["direction"] == "bullish":
            conditions_met.append({"cond": "sweep", "detail": f"Sell-Side Sweep عند ${sweep['level']}", "weight": 5})
        elif macro == "sell" and sweep["direction"] == "bearish":
            conditions_met.append({"cond": "sweep", "detail": f"Buy-Side Sweep عند ${sweep['level']}", "weight": 5})
        else:
            conditions_missing.append({"cond": "sweep", "detail": "آخر Sweep عكس الاتجاه", "weight": 5})
    else:
        conditions_missing.append({"cond": "sweep", "detail": "لا يوجد Sweep مؤخراً", "weight": 5})

    # ── حساب الثقة ───────────────────────────────────────────────────────
    score = sum(c["weight"] for c in conditions_met)
    max_score = sum(c["weight"] for c in conditions_met + conditions_missing)
    confidence = round(score / max_score * 100, 1) if max_score else 0

    if confidence >= 65 and macro == "buy":
        action = "buy"
    elif confidence >= 65 and macro == "sell":
        action = "sell"
    else:
        action = "wait"

    # SL و TP مقترحان
    h1_atr = tf_h1.get("atr", price * 0.003)
    sl = round(price - h1_atr * 1.5, 2) if action == "buy" else round(price + h1_atr * 1.5, 2)
    tp = round(price + h1_atr * 2.5, 2) if action == "buy" else round(price - h1_atr * 2.5, 2)

    return {
        "action":             action,
        "macro_bias":         macro,
        "confidence":         confidence,
        "score":              score,
        "max_score":          max_score,
        "conditions_met":     conditions_met,
        "conditions_missing": conditions_missing,
        "suggested_sl":       sl,
        "suggested_tp":       tp,
        "rr":                 round(abs(tp - price) / abs(sl - price), 2) if abs(sl - price) > 0 else 0,
    }


def full_analysis() -> dict:
    """
    التحليل الكامل — يجلب جميع الفريمات ويحلل ويعطي إشارة دخول
    """
    analyses = {}
    for name, (interval, period) in TIMEFRAMES.items():
        try:
            df = _fetch(interval, period)
            analyses[name] = _analyze_tf(df, name)
        except Exception as e:
            analyses[name] = {"error": str(e)}

    # السيولة من H1
    liq = {}
    try:
        df_h1 = _fetch("1h", "30d")
        if not df_h1.empty:
            liq = _liquidity_levels(df_h1)
    except Exception:
        pass

    entry  = _entry_signal(analyses, liq)
    price  = analyses.get("h1", {}).get("price") or analyses.get("daily", {}).get("price", 0)

    return {
        "symbol":    "XAUUSD",
        "price":     price,
        "timestamp": datetime.utcnow().isoformat(),
        "timeframes": {
            k: {
                "trend":     v.get("trend"),
                "structure": v.get("structure"),
                "rsi":       v.get("rsi"),
                "macd_hist": v.get("macd_hist"),
                "patterns":  v.get("patterns", []),
                "ema":       v.get("ema", {}),
                "sr":        v.get("sr", {}),
            }
            for k, v in analyses.items() if "error" not in v
        },
        "liquidity":     liq,
        "entry_signal":  entry,
    }
