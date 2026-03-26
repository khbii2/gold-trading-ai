"""
/api/v1/signals  — إشارات الذهب
/api/v1/data     — إدارة البيانات
"""
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from ...core.database import Session, Signal, Candle
from ...data.ingestion_ohlcv import update_data, load_candles_df, fetch_gold_ohlcv, store_candles
from ...features.technical_features import build_features
from ...models.gold_ohlcv_model import ohlcv_model
from ...models.meta_decision_model import meta_model

router = APIRouter()


# ── Signals ──────────────────────────────────────────────────────────────────

@router.get("/signals/gold")
def get_gold_signal(refresh: bool = False):
    """
    الإشارة الحالية للذهب من ML
    ?refresh=true — يجلب بيانات جديدة من yfinance أولاً
    """
    if refresh:
        try:
            update_data()
        except Exception:
            pass  # نكمل بالبيانات الموجودة في DB

    # جلب آخر 400 شمعة لبناء features (MA200 تحتاج 200+)
    df = load_candles_df()
    if df.empty:
        try:
            df = fetch_gold_ohlcv(period="60d")
        except Exception as e:
            raise HTTPException(500, f"لا بيانات: {e}")

    df = df.tail(400)
    current_price = float(df["close"].iloc[-1])

    decision = meta_model.decide(df)

    # حفظ الإشارة
    session = Session()
    try:
        sig = Signal(
            bias          = decision["bias"],
            confidence    = decision["confidence"],
            score         = decision.get("score", 0.0),
            features_json = json.dumps(decision.get("key_features", {})),
        )
        session.add(sig)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

    return {
        "symbol": "XAUUSD",
        "price":  current_price,
        **decision,
    }


@router.get("/signals/gold/history")
def signal_history(limit: int = 100):
    """آخر N إشارة"""
    session = Session()
    try:
        rows = session.query(Signal).order_by(Signal.ts.desc()).limit(limit).all()
        return [
            {
                "ts":            r.ts.isoformat(),
                "bias":          r.bias,
                "confidence":    r.confidence,
                "score":         r.score,
                "model_version": r.model_version,
                "features":      json.loads(r.features_json or "{}"),
            }
            for r in rows
        ]
    finally:
        session.close()


# ── Chart data ───────────────────────────────────────────────────────────────

import numpy as _np
from ...features.indicators import ema as _ema
from ...features.candle_patterns import detect_patterns as _det_pat
from ...features.multi_tf_analysis import _support_resistance as _sr, _liquidity_levels as _liq
from ...features.fibonacci import golden_zone_analysis as _fib_analysis
from ...data.provider import fetch_ohlcv as _fetch_ohlcv

# TF key → provider key mapping
_TF_KEY = {
    "1m": "1m", "5m": "5m", "15m": "15m",
    "1h": "1h", "4h": "4h", "1d":  "1d", "1w": "1w",
}


@router.get("/chart/data")
def chart_data(tf: str = "1h", limit: int = 300):
    """OHLCV + EMAs + S/R + Liquidity + Patterns + Fibonacci — كل فريم"""
    provider_tf = _TF_KEY.get(tf, "1h")
    try:
        df = _fetch_ohlcv(provider_tf, limit=limit, use_cache=True)
    except Exception as e:
        raise HTTPException(500, str(e))

    if df.empty:
        raise HTTPException(404, "no data")

    c = df["close"]

    # ── Candles ──
    candles = []
    for ts, row in df.iterrows():
        t = int(ts.timestamp()) if hasattr(ts, "timestamp") else int(ts)
        candles.append({"time": t, "open": round(float(row["open"]), 2),
                        "high": round(float(row["high"]), 2),
                        "low":  round(float(row["low"]),  2),
                        "close": round(float(row["close"]), 2)})

    times = [cd["time"] for cd in candles]

    def _ema_series(period):
        vals = _ema(c, period).values
        return [{"time": t, "value": round(float(v), 2)}
                for t, v in zip(times, vals) if not _np.isnan(v)]

    # ── S/R + Liquidity ──
    sr  = _sr(df)
    liq = _liq(df)

    # ── Pattern markers ──
    markers = []
    for i in range(2, len(df)):
        chunk = df.iloc[max(0, i-2): i+1]
        pats  = _det_pat(chunk)
        for p in pats:
            t = candles[i]["time"]
            markers.append({
                "time":     t,
                "position": "belowBar" if p["direction"] == "bullish" else "aboveBar",
                "color":    "#00e5a0" if p["direction"] == "bullish" else "#ff4466",
                "shape":    "arrowUp" if p["direction"] == "bullish" else "arrowDown",
                "text":     p["pattern"],
            })

    # ── Fibonacci + Order Blocks ──
    fib = _fib_analysis(df)

    return {
        "candles":     candles,
        "ema9":        _ema_series(9),
        "ema20":       _ema_series(20),
        "ema50":       _ema_series(50),
        "ema200":      _ema_series(200),
        "resistances": sr.get("resistances", []),
        "supports":    sr.get("supports",    []),
        "buy_side":    liq.get("buy_side",   [])[:4],
        "sell_side":   liq.get("sell_side",  [])[:4],
        "equal_highs": liq.get("equal_highs", []),
        "equal_lows":  liq.get("equal_lows",  []),
        "last_sweep":  liq.get("last_sweep"),
        "markers":     markers,
        # Fibonacci data
        "fib": {
            "swing_high":    fib.get("swing_high"),
            "swing_low":     fib.get("swing_low"),
            "direction":     fib.get("direction"),
            "levels":        fib.get("fib_levels", {}),
            "golden_zone":   fib.get("golden_zone"),
            "in_golden_zone": fib.get("in_golden_zone", False),
            "order_blocks":  fib.get("order_blocks", []),
            "ob_in_gz":      fib.get("ob_in_golden_zone", False),
            "sweep":         fib.get("sweep_confirmed", False),
            "quality":       fib.get("entry_quality", 0),
            "signal":        fib.get("entry_signal"),
            "conditions":    fib.get("conditions", []),
        },
    }


# ── Fibonacci standalone endpoint ─────────────────────────────────────────────

@router.get("/fib/gold")
def fib_analysis(tf: str = "15m"):
    """
    Fibonacci retracement + Golden Zone + Order Block analysis
    Default: 15M (الفريم المستخدم في الاستراتيجية)
    """
    provider_tf = _TF_KEY.get(tf, "15m")
    try:
        df = _fetch_ohlcv(provider_tf, limit=300)
    except Exception as e:
        raise HTTPException(500, str(e))

    if df is None or df.empty:
        raise HTTPException(404, "no data")

    result = _fib_analysis(df)
    result["tf"] = tf
    result["price"] = float(df["close"].iloc[-1])
    return result


# ── Data management ───────────────────────────────────────────────────────────

@router.post("/data/update")
def trigger_data_update():
    """تحديث البيانات يدوياً"""
    result = update_data()
    return result


@router.get("/data/status")
def data_status():
    session = Session()
    try:
        n     = session.query(Candle).count()
        first = session.query(Candle).order_by(Candle.ts).first()
        last  = session.query(Candle).order_by(Candle.ts.desc()).first()
        return {
            "total_candles": n,
            "first_ts":      first.ts.isoformat() if first else None,
            "last_ts":       last.ts.isoformat()  if last  else None,
        }
    finally:
        session.close()


# ── Model training ────────────────────────────────────────────────────────────

_training_status = {"running": False, "last_result": None}

def _do_train():
    _training_status["running"] = True
    try:
        result = update_data()
        df = load_candles_df()
        if df.empty:
            df = fetch_gold_ohlcv(period="2y")
            store_candles(df)
            df = load_candles_df()
        features_df = build_features(df)
        metrics = ohlcv_model.train(features_df)
        _training_status["last_result"] = {"status": "ok", "metrics": metrics}
    except Exception as e:
        _training_status["last_result"] = {"status": "error", "error": str(e)}
    finally:
        _training_status["running"] = False

@router.post("/model/train")
def train_model(background_tasks: BackgroundTasks):
    """تدريب النموذج في الخلفية — استدعِه مرة واحدة بعد الـ deploy"""
    if _training_status["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(_do_train)
    return {"status": "started", "message": "التدريب بدأ — استدعِ /model/status لمتابعة"}

@router.get("/model/status")
def model_status():
    """حالة التدريب + metrics النموذج"""
    if ohlcv_model.is_trained and not ohlcv_model.metrics:
        ohlcv_model.load()
    return {
        "trained":         ohlcv_model.is_trained,
        "training_running": _training_status["running"],
        "last_result":     _training_status["last_result"],
        "metrics":         ohlcv_model.metrics,
    }
