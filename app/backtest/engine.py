"""
Backtesting Engine v0 — Phase 7
يعيد تشغيل إشارات OHLCV model على البيانات التاريخية
"""
import pandas as pd
import numpy as np
from ..features.technical_features import build_features, FEATURE_COLS
from ..models.gold_ohlcv_model import ohlcv_model


def run_backtest(
    df:              pd.DataFrame,
    initial_capital: float = 10_000.0,
    risk_per_trade:  float = 0.01,   # 1%
    rr:              float = 1.5,    # TP = 1.5 × SL
    min_confidence:  float = 0.55,   # تجاهل الإشارات الضعيفة
) -> dict:
    """
    Backtest بسيط على OHLCV
    يفترض: SL محدد، TP = SL * rr، كل صفقة تخاطر بـ risk_per_trade% من الرأسمال
    """
    if not ohlcv_model.is_trained:
        return {"error": "النموذج غير مدرب — شغّل train_model.py أولاً"}

    features_df = build_features(df)
    if features_df.empty:
        return {"error": "لا بيانات كافية لبناء features"}

    cols = [c for c in FEATURE_COLS if c in features_df.columns]

    # التقييم على بيانات التحقق فقط (لا data leakage)
    split       = int(len(features_df) * 0.8)
    val_df      = features_df.iloc[split:]

    X      = val_df[cols].values
    labels = val_df["label"].values
    probas = ohlcv_model.model.predict_proba(X)
    preds  = ohlcv_model.model.predict(X)

    capital = initial_capital
    trades  = []

    for pred, label, proba in zip(preds, labels, probas):
        conf = float(max(proba))
        if conf < min_confidence:
            continue

        risk_amt = capital * risk_per_trade
        won      = bool(pred == label)
        pnl      = risk_amt * rr if won else -risk_amt
        capital += pnl

        trades.append({"won": won, "pnl": pnl, "capital": capital})

    if not trades:
        return {"error": "لا صفقات — جرّب تخفيض min_confidence"}

    t           = pd.DataFrame(trades)
    wins        = int(t["won"].sum())
    total       = len(t)
    total_ret   = (capital - initial_capital) / initial_capital
    peak        = t["capital"].cummax()
    drawdown    = (t["capital"] - peak) / peak
    max_dd      = float(drawdown.min())
    gross_win   = t.loc[t["pnl"] > 0, "pnl"].sum()
    gross_loss  = abs(t.loc[t["pnl"] < 0, "pnl"].sum())

    return {
        "total_trades":       total,
        "wins":               wins,
        "losses":             total - wins,
        "win_rate":           round(wins / total, 4),
        "total_return_pct":   round(total_ret * 100, 2),
        "final_capital":      round(capital, 2),
        "max_drawdown_pct":   round(max_dd * 100, 2),
        "expectancy_per_R":   round((wins / total * rr) - (1 - wins / total), 4),
        "profit_factor":      round(gross_win / gross_loss, 2) if gross_loss > 0 else None,
        "params": {
            "initial_capital": initial_capital,
            "risk_per_trade":  risk_per_trade,
            "rr":              rr,
            "min_confidence":  min_confidence,
        },
    }
