"""Completed trade. Side is always from the market maker's perspective."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CompletedTrade:
    ticker: str
    trade_volume: int
    trade_price: float
    mm_action: str
    ref_price: float
    bid_price: float
    offer_price: float
    date: object

    def __post_init__(self) -> None:
        if not self.ticker or type(self.trade_volume) is not int or self.trade_volume <= 0:
            raise ValueError("positive integer trade volume required")
        if self.mm_action.lower() not in {"buy", "sell"}:
            raise ValueError("mm_action must be buy or sell")
        if not all(math.isfinite(x) and x > 0 for x in
                   (self.trade_price, self.ref_price, self.bid_price, self.offer_price)):
            raise ValueError("positive finite prices required")
        if self.bid_price > self.offer_price:
            raise ValueError("bid exceeds offer")
        expected = self.bid_price if self.mm_action.lower() == "buy" else self.offer_price
        if not math.isclose(self.trade_price, expected, rel_tol=1e-10):
            raise ValueError("execution price must equal the quoted side")
