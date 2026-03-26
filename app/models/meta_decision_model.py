"""
Meta-Decision Model — يجمع الإشارات من كل النماذج

Phase 3  : OHLCV فقط (الآن)
Phase 5  : + OrderFlow model
Phase 6  : + SMC/Structure + News/Macro
Phase 7  : Ensemble / stacking

لإضافة نموذج جديد: افتح التعليق في _collect_signals()
"""
from datetime import datetime
from ..features.technical_features import build_features
from .gold_ohlcv_model import ohlcv_model


class MetaDecisionModel:

    def decide(self, df) -> dict:
        """
        القرار النهائي للذهب
        df   : DataFrame OHLCV (آخر N شمعة)
        Returns dict: bias, confidence, score, reasons, key_features, ts
        """
        features_df = build_features(df)
        if features_df.empty:
            return self._neutral(["no_data"])

        latest  = features_df.iloc[-1].to_dict()
        signals = []    # list of (weighted_score)
        weights = []
        reasons = []

        # ── OHLCV Model ──────────────────────────────────────────────────────
        if ohlcv_model.is_trained:
            try:
                bias, conf = ohlcv_model.predict_proba(latest)
                direction  = 1 if bias == "buy" else (-1 if bias == "sell" else 0)
                signals.append(direction * conf)
                weights.append(1.0)
                reasons.append(f"ohlcv_v0:{bias}@{conf:.2f}")
            except Exception as e:
                reasons.append(f"ohlcv_err:{e}")
        else:
            reasons.append("ohlcv_not_trained — run train_model.py")

        # ── Order Flow Model (Phase 5 — placeholder) ─────────────────────────
        # if of_model.is_trained:
        #     bias_of, conf_of = of_model.predict(of_features)
        #     signals.append((1 if bias_of=="buy" else -1) * conf_of)
        #     weights.append(1.2)
        #     reasons.append(f"orderflow:{bias_of}@{conf_of:.2f}")

        # ── SMC / Structure (Phase 6 — placeholder) ──────────────────────────
        # ── News / Macro (Phase 6 — placeholder) ─────────────────────────────

        if not signals:
            return self._neutral(reasons)

        total_w = sum(weights)
        score   = sum(s * w for s, w in zip(signals, weights)) / total_w

        if score > 0.12:
            bias, conf = "buy",  round(min(0.5 + score, 1.0), 4)
        elif score < -0.12:
            bias, conf = "sell", round(min(0.5 - score, 1.0), 4)
        else:
            bias, conf = "neutral", round(0.5 + abs(score), 4)

        key = {
            "rsi_14":    round(latest.get("rsi_14", 0) * 100, 1),
            "ret_1h":    round(latest.get("ret_1h",  0) * 100, 3),
            "ret_24h":   round(latest.get("ret_24h", 0) * 100, 2),
            "ma20_ratio":round(latest.get("ma20_ratio", 1), 4),
            "atr_norm":  round(latest.get("atr_norm", 0) * 100, 3),
            "bb_width":  round(latest.get("bb_width", 0) * 100, 3),
        }

        return {
            "bias":         bias,
            "confidence":   conf,
            "score":        round(score, 4),
            "reasons":      reasons,
            "key_features": key,
            "ts":           datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _neutral(reasons: list) -> dict:
        return {
            "bias":         "neutral",
            "confidence":   0.0,
            "score":        0.0,
            "reasons":      reasons,
            "key_features": {},
            "ts":           datetime.utcnow().isoformat(),
        }


meta_model = MetaDecisionModel()
