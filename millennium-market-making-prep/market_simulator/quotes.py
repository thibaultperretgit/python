"""Quote representation and symmetric reference pricing."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class QuotedTrade:
    ticker: str
    trade_volume: int
    ref_price: float
    bid_price: float
    offer_price: float
    date: object

    def __post_init__(self) -> None:
        if not self.ticker or isinstance(self.trade_volume, bool) or not isinstance(self.trade_volume, int) or self.trade_volume <= 0:
            raise ValueError("ticker and positive integer volume required")
        if not all(math.isfinite(x) for x in (self.ref_price, self.bid_price, self.offer_price)):
            raise ValueError("prices must be finite")
        if self.ref_price <= 0 or self.bid_price <= 0 or self.bid_price > self.offer_price:
            raise ValueError("require 0 < bid <= offer and positive reference")


def make_quote(ticker: str, volume: int, mid: float, date: object,
               spread_fraction: float = 0.02, skew_fraction: float = 0.0) -> QuotedTrade:
    """Full spread is spread_fraction; positive skew shifts both sides down."""
    if not math.isfinite(spread_fraction) or not 0 < spread_fraction < 2:
        raise ValueError("spread_fraction must be in (0, 2)")
    if not math.isfinite(skew_fraction):
        raise ValueError("skew_fraction must be finite")
    center = mid * (1 - skew_fraction)
    half = mid * spread_fraction / 2
    return QuotedTrade(ticker, volume, mid, center - half, center + half, date)
