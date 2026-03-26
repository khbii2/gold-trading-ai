"""
Live price WebSocket — تحديث لحظي كل ثانيتين
"""
import asyncio
import time
import yfinance as yf
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Cache بسيط — يجلب كل 8 ثوانٍ فقط
_cache: dict = {"price": 0.0, "prev": 0.0, "high": 0.0, "low": 0.0, "change_pct": 0.0, "ts": 0.0}


def _refresh_price():
    now = time.time()
    if now - _cache["ts"] < 8:
        return
    try:
        df = yf.download("GC=F", period="2d", interval="1m", progress=False, auto_adjust=True)
        if isinstance(df, tuple): df = df[0]
        if df.empty: return
        df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]
        price  = float(df["close"].iloc[-1])
        open_d = float(df["close"].iloc[-390]) if len(df) > 390 else float(df["close"].iloc[0])
        _cache.update({
            "prev":       _cache["price"] or price,
            "price":      price,
            "high":       float(df["high"].tail(390).max()),
            "low":        float(df["low"].tail(390).min()),
            "change_pct": round((price - open_d) / open_d * 100, 3),
            "ts":         now,
        })
    except Exception:
        pass


@router.get("/price/live")
def get_live_price():
    _refresh_price()
    return {
        "price":      round(_cache["price"], 2),
        "prev":       round(_cache["prev"], 2),
        "high":       round(_cache["high"], 2),
        "low":        round(_cache["low"], 2),
        "change_pct": _cache["change_pct"],
        "direction":  "up" if _cache["price"] >= _cache["prev"] else "down",
    }


@router.websocket("/ws/price")
async def ws_price(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            _refresh_price()
            await websocket.send_json({
                "price":      round(_cache["price"], 2),
                "prev":       round(_cache["prev"], 2),
                "high":       round(_cache["high"], 2),
                "low":        round(_cache["low"], 2),
                "change_pct": _cache["change_pct"],
                "direction":  "up" if _cache["price"] >= _cache["prev"] else "down",
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
