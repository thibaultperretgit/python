"""Commission-aware account used by the ETF arbitrage practice challenge."""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import pandas as pd


@dataclass
class CurrentPosition:
    ticker: str
    direction: str = "FLAT"
    position_volume: float = 0.0
    open_price: float = 0.0
    profit_loss: float = 0.0
    commission_costs: float = 0.0
    trade_history: list[dict[str, object]] = field(default_factory=list)
    date: object = 0


class ArbitrageHedgeFund:
    """Immediate-fill account with cash, positions, commissions, and histories."""

    def __init__(self, commission_percentage: float, data: pd.DataFrame,
                 initial_balance: float = 20_000_000.0) -> None:
        if not 0 <= commission_percentage < 1:
            raise ValueError("commission_percentage must be in [0, 1)")
        if not isinstance(data, pd.DataFrame) or data.empty:
            raise ValueError("data must be a non-empty price DataFrame")
        if not math.isfinite(initial_balance):
            raise ValueError("initial_balance must be finite")
        numeric = data.astype(float)
        if not (numeric.to_numpy() > 0).all():
            raise ValueError("all prices must be positive")
        self.commission_percentage = float(commission_percentage)
        self.data = numeric.copy()
        self.initial_balance = float(initial_balance)
        self.balance = float(initial_balance)
        self.current_positions = {
            str(ticker): CurrentPosition(str(ticker)) for ticker in self.data.columns
        }

    @classmethod
    def hf(cls, commission_percentage: float = 0.001,
           data: pd.DataFrame | None = None,
           initial_balance: float = 20_000_000.0) -> "ArbitrageHedgeFund":
        if data is None:
            raise ValueError("data is required")
        return cls(commission_percentage, data, initial_balance)

    def execute_order(self, ticker: str, volume: float, action: str, date: object):
        ticker = str(ticker)
        action_lower = str(action).lower()
        if ticker not in self.current_positions:
            raise ValueError(f"unknown ticker: {ticker}")
        if action_lower not in {"buy", "sell"}:
            raise ValueError("action must be buy or sell")
        if not math.isfinite(float(volume)) or volume <= 0:
            raise ValueError("volume must be positive and finite")
        if date not in self.data.index:
            raise ValueError(f"date not in price data: {date}")

        volume = float(volume)
        price = float(self.data.loc[date, ticker])
        fee = price * volume * self.commission_percentage
        delta = volume if action_lower == "buy" else -volume
        position = self.current_positions[ticker]
        old_signed = (position.position_volume if position.direction == "LONG" else
                      -position.position_volume if position.direction == "SHORT" else 0.0)
        new_signed = old_signed + delta

        realized = 0.0
        if old_signed == 0 or old_signed * delta > 0:
            new_open = ((abs(old_signed) * position.open_price + abs(delta) * price)
                        / abs(new_signed))
        else:
            closed = min(abs(old_signed), abs(delta))
            realized = closed * (price - position.open_price) * (1.0 if old_signed > 0 else -1.0)
            if new_signed == 0:
                new_open = 0.0
            elif old_signed * new_signed < 0:
                new_open = price
            else:
                new_open = position.open_price

        position.direction = "LONG" if new_signed > 0 else "SHORT" if new_signed < 0 else "FLAT"
        position.position_volume = abs(new_signed)
        position.open_price = new_open
        position.profit_loss += realized
        position.commission_costs += fee
        position.date = date
        record = {
            "action": action_lower.upper(),
            "price": price,
            "volume": volume,
            "commission": fee,
            "date": date,
        }
        position.trade_history.append(record)
        self.balance -= delta * price + fee
        return record
