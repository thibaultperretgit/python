"""Small deterministic exchange facade for ETF hedge exercises."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ExchangeTrade:
    ticker: str
    trade_volume: float
    ref_price: float
    action: str
    date: object

    def __post_init__(self) -> None:
        if not self.ticker or not math.isfinite(float(self.trade_volume)) or self.trade_volume <= 0:
            raise ValueError("ticker and positive volume required")
        if not math.isfinite(float(self.ref_price)) or self.ref_price <= 0:
            raise ValueError("positive finite reference price required")
        if self.action.lower() not in {"buy", "sell"}:
            raise ValueError("action must be buy or sell")


@dataclass(frozen=True)
class ExecutedTrade:
    ticker: str
    trade_volume: float
    trade_price: float
    action: str
    date: object
    ref_price: float


class Exchange:
    """Execute a market hedge immediately at its supplied reference price."""

    slippage_bps = 0.0

    @classmethod
    def execute(cls, trade: ExchangeTrade) -> ExecutedTrade:
        if not all(hasattr(trade, field) for field in
                   ("ticker", "trade_volume", "ref_price", "action", "date")):
            raise TypeError("trade must provide ticker, volume, price, action, and date")
        validated = ExchangeTrade(
            str(trade.ticker), float(trade.trade_volume), float(trade.ref_price),
            str(trade.action), trade.date,
        )
        direction = 1.0 if validated.action.lower() == "buy" else -1.0
        price = validated.ref_price * (1.0 + direction * cls.slippage_bps / 10_000.0)
        return ExecutedTrade(
            validated.ticker, validated.trade_volume, price,
            validated.action.lower(), validated.date, validated.ref_price,
        )
