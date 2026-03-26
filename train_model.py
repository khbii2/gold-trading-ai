#!/usr/bin/env python3
"""
train_model.py — تدريب نموذج OHLCV v0
شغّله مرة واحدة قبل تشغيل الـ API

    python train_model.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db
from app.data.ingestion_ohlcv import update_data, load_candles_df, fetch_gold_ohlcv, store_candles
from app.features.technical_features import build_features
from app.models.gold_ohlcv_model import ohlcv_model
from app.backtest.engine import run_backtest


def main():
    sep = "═" * 55
    print(sep)
    print("  Gold Trading AI — تدريب نموذج OHLCV v0")
    print(sep)

    # ── 1. تهيئة DB ──────────────────────────────────────────────────────────
    init_db()

    # ── 2. جلب البيانات ───────────────────────────────────────────────────────
    print("\n[1/4] جلب بيانات الذهب (yfinance GC=F)...")
    try:
        r = update_data()
        print(f"  ✅ {r['fetched']:,} شمعة | {r['stored_new']:,} جديدة")
    except Exception as e:
        print(f"  ⚠️  {e}")
        print("  جلب مباشر من yfinance...")
        df_raw = fetch_gold_ohlcv(period="2y")
        n = store_candles(df_raw)
        print(f"  ✅ {len(df_raw):,} شمعة | {n:,} مخزّنة")

    # ── 3. بناء features ──────────────────────────────────────────────────────
    print("\n[2/4] تحميل البيانات وبناء features...")
    df = load_candles_df()
    if df.empty:
        print("  ❌ لا توجد بيانات في DB")
        return

    features_df = build_features(df)
    print(f"  ✅ {len(df):,} شمعة → {len(features_df):,} صف بعد dropna")
    print(f"  Features: {[c for c in features_df.columns if c != 'label']}")

    # ── 4. تدريب ─────────────────────────────────────────────────────────────
    print("\n[3/4] تدريب RandomForest...")
    metrics = ohlcv_model.train(features_df)

    print(f"\n  {'─'*40}")
    print(f"  دقة التحقق  : {metrics['accuracy']*100:6.2f}%")
    print(f"  Hit Rate    : {metrics['hit_rate']*100:6.2f}%")
    print(f"  Expectancy  : {metrics['expectancy_per_R']:+.3f}R  (1R = SL, TP = 1.5R)")
    print(f"  Train       : {metrics['train_samples']:,} شمعة")
    print(f"  Validation  : {metrics['val_samples']:,} شمعة")
    print(f"  {'─'*40}")

    # ── 5. Backtest ───────────────────────────────────────────────────────────
    print("\n[4/4] Backtest سريع على بيانات التحقق...")
    bt = run_backtest(df, initial_capital=10_000)
    if "error" in bt:
        print(f"  ⚠️  {bt['error']}")
    else:
        print(f"  صفقات    : {bt['total_trades']:,}")
        print(f"  Win Rate : {bt['win_rate']*100:.1f}%")
        print(f"  عائد كلي : {bt['total_return_pct']:+.2f}%")
        print(f"  Max DD   : {bt['max_drawdown_pct']:.2f}%")
        print(f"  PF       : {bt.get('profit_factor', 'N/A')}")

    print(f"\n  ✅ النموذج محفوظ: data/models/gold_ohlcv_v0.joblib")
    print(sep)
    print("  التالي: uvicorn app.main:app --reload --port 8000")
    print(sep)


if __name__ == "__main__":
    main()
