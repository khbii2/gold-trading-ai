"""
Live price WebSocket — تحديث لحظي كل ثانيتين
يستخدم fast_info للسعر اللحظي (أقل تأخراً من download)
"""
import asyncio
import time
import yfinance as yf
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

_cache: dict = {"price": 0.0, "prev": 0.0, "high": 0.0, "low": 0.0, "change_pct": 0.0, "ts": 0.0}
_TICKER = yf.Ticker("GC=F")


def _refresh_price():
    now = time.time()
    if now - _cache["ts"] < 5:   # cache 5s
        return
    try:
        fi = _TICKER.fast_info
        price = float(fi.last_price or 0)
        if price < 100:            # fallback: download 1m
            raise ValueError("bad fast_info price")
        prev  = float(fi.previous_close or price)
        high  = float(fi.day_high  or price)
        low   = float(fi.day_low   or price)
        chg   = round((price - prev) / prev * 100, 3) if prev else 0.0
        _cache.update({
            "prev":       _cache["price"] or prev,
            "price":      price,
            "high":       high,
            "low":        low,
            "change_pct": chg,
            "ts":         now,
        })
    except Exception:
        # fallback to 1m bar
        try:
            df = yf.download("GC=F", period="1d", interval="1m",
                             progress=False, auto_adjust=True)
            if isinstance(df, tuple): df = df[0]
            if df.empty: return
            df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower()
                          for c in df.columns]
            price  = float(df["close"].iloc[-1])
            open_d = float(df["close"].iloc[0])
            _cache.update({
                "prev":       _cache["price"] or price,
                "price":      price,
                "high":       float(df["high"].max()),
                "low":        float(df["low"].min()),
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
        "prev":       round(_cache["prev"],  2),
        "high":       round(_cache["high"],  2),
        "low":        round(_cache["low"],   2),
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
                "prev":       round(_cache["prev"],  2),
                "high":       round(_cache["high"],  2),
                "low":        round(_cache["low"],   2),
                "change_pct": _cache["change_pct"],
                "direction":  "up" if _cache["price"] >= _cache["prev"] else "down",
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
