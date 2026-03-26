"""
Risk Engine — Phase 9
حسابات إدارة المخاطر لـ FTMO / أي بروكر

حالياً: حسابات + قواعد فقط (لا ربط بـ broker API)
المرحلة 9 ستضيف: broker_api.py + auto-execution
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class RiskConfig:
    # FTMO parameters (default)
    account_balance:     float = 10_000.0
    max_risk_per_trade:  float = 0.01     # 1%
    max_daily_loss:      float = 0.05     # 5%  — FTMO hard limit
    max_total_loss:      float = 0.10     # 10% — FTMO challenge limit
    max_open_trades:     int   = 1        # conservative: 1 at a time
    min_rr:              float = 1.5      # minimum reward:risk


class RiskEngine:

    def __init__(self, config: Optional[RiskConfig] = None):
        self.config      = config or RiskConfig()
        self.daily_loss  = 0.0
        self.total_loss  = 0.0
        self.open_trades = 0
        self.today       = date.today()

    # ── Checks ───────────────────────────────────────────────────────────────

    def can_open_trade(self) -> tuple[bool, str]:
        """هل يمكن فتح صفقة جديدة؟"""
        self._reset_daily_if_needed()

        if self.daily_loss >= self.config.max_daily_loss:
            return False, f"تجاوز الحد اليومي {self.config.max_daily_loss*100:.0f}%"
        if self.total_loss >= self.config.max_total_loss:
            return False, f"تجاوز الحد الكلي {self.config.max_total_loss*100:.0f}%"
        if self.open_trades >= self.config.max_open_trades:
            return False, f"الحد الأقصى للصفقات المفتوحة: {self.config.max_open_trades}"
        return True, "ok"

    # ── Position sizing ───────────────────────────────────────────────────────

    def size(self, entry: float, stop_loss: float) -> dict:
        """
        حساب حجم الصفقة + TP بناءً على المخاطرة
        للذهب: lot = risk_amount / (|entry - stop_loss| في نقطة)
        """
        risk_amount = self.config.account_balance * self.config.max_risk_per_trade
        pips_risk   = abs(entry - stop_loss)

        if pips_risk < 0.01:
            return {"error": "المسافة بين Entry و SL صغيرة جداً"}

        lot_size   = risk_amount / pips_risk
        direction  = 1 if stop_loss < entry else -1
        take_profit = entry + direction * pips_risk * self.config.min_rr

        return {
            "lot_size":    round(lot_size, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_pct":    self.config.max_risk_per_trade * 100,
            "entry":       entry,
            "stop_loss":   stop_loss,
            "take_profit": round(take_profit, 2),
            "rr":          self.config.min_rr,
        }

    # ── State management ──────────────────────────────────────────────────────

    def record_trade_closed(self, pnl_pct: float):
        if pnl_pct < 0:
            self.daily_loss += abs(pnl_pct)
            self.total_loss += abs(pnl_pct)
        if self.open_trades > 0:
            self.open_trades -= 1

    def record_trade_opened(self):
        self.open_trades += 1

    def _reset_daily_if_needed(self):
        today = date.today()
        if today != self.today:
            self.daily_loss = 0.0
            self.today      = today

    def status(self) -> dict:
        self._reset_daily_if_needed()
        return {
            "daily_loss_pct": round(self.daily_loss * 100, 2),
            "total_loss_pct": round(self.total_loss * 100, 2),
            "open_trades":    self.open_trades,
            "can_trade":      self.can_open_trade()[0],
        }


risk_engine = RiskEngine()
