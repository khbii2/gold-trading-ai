"""
Gold OHLCV Model v0 — Phase 3
RandomForest لتوقع اتجاه الشمعة القادمة (buy/sell/neutral)

مدخلات : FEATURE_COLS التقنية من OHLCV
المخرجات: bias (buy|sell|neutral) + confidence
"""
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

from ..core.config import settings
from ..features.technical_features import FEATURE_COLS

MODEL_PATH   = settings.MODEL_DIR / "gold_ohlcv_v0.joblib"
METRICS_PATH = settings.MODEL_DIR / "gold_ohlcv_v0_metrics.json"


class GoldOHLCVModel:
    """
    نموذج OHLCV v0
    ──────────────
    Train  : قسّم زمني 80/20 — لا shuffle
    Predict: يرجع (bias, confidence)
    Save   : joblib + JSON metrics
    """

    def __init__(self):
        self.model:      Pipeline | None = None
        self.metrics:    dict            = {}
        self.version:    str             = "ohlcv_v0"
        self.trained_at: str | None      = None

    # ── Build ───────────────────────────────────────────────────────────────

    def _pipeline(self) -> Pipeline:
        return Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators  = settings.N_ESTIMATORS,
                max_depth     = 8,
                min_samples_leaf = 20,
                random_state  = settings.RANDOM_STATE,
                n_jobs        = -1,
            )),
        ])

    # ── Train ────────────────────────────────────────────────────────────────

    def train(self, features_df: pd.DataFrame) -> dict:
        """
        تدريب النموذج
        features_df يجب أن يأتي من build_features() — يشمل 'label'
        """
        cols = [c for c in FEATURE_COLS if c in features_df.columns]
        X = features_df[cols].values
        y = features_df["label"].values

        # تقسيم زمني صارم
        split    = int(len(X) * settings.TRAIN_RATIO)
        X_tr, X_v = X[:split], X[split:]
        y_tr, y_v = y[:split], y[split:]

        self.model = self._pipeline()
        self.model.fit(X_tr, y_tr)

        y_pred   = self.model.predict(X_v)
        acc      = accuracy_score(y_v, y_pred)
        hit_rate = float((y_pred == y_v).mean())

        # Expectancy при RR = 1.5
        expectancy = hit_rate * 1.5 - (1 - hit_rate)

        self.trained_at = datetime.utcnow().isoformat()
        self.metrics = {
            "accuracy":          round(acc, 4),
            "hit_rate":          round(hit_rate, 4),
            "expectancy_per_R":  round(expectancy, 4),
            "train_samples":     len(X_tr),
            "val_samples":       len(X_v),
            "feature_cols":      cols,
            "trained_at":        self.trained_at,
            "version":           self.version,
        }
        self._save()
        return self.metrics

    # ── Predict ──────────────────────────────────────────────────────────────

    def predict_proba(self, features: dict) -> tuple[str, float]:
        """
        Returns (bias, confidence)
        bias: "buy" | "sell" | "neutral"
        """
        if self.model is None:
            self.load()
        if self.model is None:
            return "neutral", 0.5

        cols = [c for c in FEATURE_COLS if c in features]
        x    = np.array([[features[c] for c in cols]])

        proba = self.model.predict_proba(x)[0]
        p_up  = float(proba[1]) if len(proba) > 1 else 0.5

        if p_up >= 0.60:
            return "buy",  round(p_up, 4)
        elif p_up <= 0.40:
            return "sell", round(1.0 - p_up, 4)
        else:
            return "neutral", round(max(p_up, 1.0 - p_up), 4)

    # ── Persistence ──────────────────────────────────────────────────────────

    def _save(self):
        settings.MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        with open(METRICS_PATH, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def load(self) -> bool:
        if not MODEL_PATH.exists():
            return False
        self.model = joblib.load(MODEL_PATH)
        if METRICS_PATH.exists():
            with open(METRICS_PATH) as f:
                self.metrics = json.load(f)
        return True

    @property
    def is_trained(self) -> bool:
        return MODEL_PATH.exists()


# Singleton
ohlcv_model = GoldOHLCVModel()
