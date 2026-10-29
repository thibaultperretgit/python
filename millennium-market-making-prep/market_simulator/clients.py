"""Simple synthetic client response model, not a proprietary hedge fund model."""
from dataclasses import dataclass
import math
import numpy as np
from .quotes import QuotedTrade


@dataclass(frozen=True)
class HfResponse:
    ticker: str
    trade_volume: int
    trade_price: float | None
    hf_action: str  # buy, sell, or refuse from the client's perspective.
    ref_price: float
    bid_price: float
    offer_price: float
    date: object

    def __str__(self) -> str:
        return (f"Hedge Fund Response for {self.ticker}, {self.trade_volume} shares "
                f"@ {self.ref_price} on {self.date}. Bid Price: {self.bid_price} and "
                f"Offer Price: {self.offer_price}. Hedge Fund Decisions: "
                f"{self.trade_price}, {self.hf_action}")

    def __repr__(self) -> str:
        return (f"HfResponse(ticker={self.ticker}, trade_volume={self.trade_volume}, "
                f"trade_price={self.trade_price}, hf_action={self.hf_action}, "
                f"ref_price={self.ref_price}, bid_price={self.bid_price}, "
                f"offer_price={self.offer_price}, date={self.date})")


class ClientModel:
    def __init__(self, seed: int = 0, buy_probability: float = 0.5,
                 base_acceptance: float = 0.7, sensitivity: float = 35.0) -> None:
        if not 0 <= buy_probability <= 1 or not 0 <= base_acceptance <= 1 or sensitivity < 0:
            raise ValueError("invalid client probabilities or sensitivity")
        self.rng = np.random.default_rng(seed)
        self.buy_probability = buy_probability
        self.base_acceptance = base_acceptance
        self.sensitivity = sensitivity

    def acceptance_probability(self, quote: QuotedTrade, side: str) -> float:
        """A cheaper ask or higher bid improves the client's acceptance chance."""
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        advantage = ((quote.ref_price - quote.offer_price) if side == "buy" else
                     (quote.bid_price - quote.ref_price)) / quote.ref_price
        return float(min(1, max(0, self.base_acceptance * math.exp(self.sensitivity * advantage))))

    def show(self, quote: QuotedTrade) -> HfResponse:
        side = "buy" if self.rng.random() < self.buy_probability else "sell"
        accepted = self.rng.random() < self.acceptance_probability(quote, side)
        action = side if accepted else "refuse"
        price = (quote.offer_price if side == "buy" else quote.bid_price) if accepted else None
        return HfResponse(quote.ticker, quote.trade_volume, price, action,
                          quote.ref_price, quote.bid_price, quote.offer_price, quote.date)
