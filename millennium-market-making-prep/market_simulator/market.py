"""Seeded synthetic prices, RFQs, and sequential market-making simulation."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from .market_maker import MarketMaker
from .clients import ClientModel
from .trades import CompletedTrade


@dataclass(frozen=True)
class RFQ:
    timestamp: pd.Timestamp
    ticker: str
    quantity: int

    def __post_init__(self):
        if not self.ticker or type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("RFQ needs a ticker and positive integer quantity")


def generate_market_data(tickers=("ALFA", "BETA", "GAMMA"), periods=100,
                         seed=42, volatility=0.015, start_price=100.0,
                         spread_fraction=0.002) -> pd.DataFrame:
    """Independent lognormal paths. Volatility is per step, not annualized."""
    if periods <= 0 or not tickers or len(set(tickers)) != len(tickers) or any(not t for t in tickers):
        raise ValueError("positive periods and unique nonempty tickers required")
    if volatility < 0 or start_price <= 0 or not 0 < spread_fraction < 2:
        raise ValueError("invalid volatility, start price, or spread")
    rng = np.random.default_rng(seed)
    steps = rng.normal(-0.5 * volatility**2, volatility, size=(periods - 1, len(tickers)))
    mids = np.vstack([np.full(len(tickers), start_price),
                      start_price * np.exp(np.cumsum(steps, axis=0))])
    times = pd.date_range("2026-01-02 09:30", periods=periods, freq="min", tz="UTC")
    records = []
    for i, timestamp in enumerate(times):
        for j, ticker in enumerate(tickers):
            mid = float(mids[i, j])
            records.append((timestamp, ticker, mid, mid * (1 - spread_fraction/2), mid * (1 + spread_fraction/2)))
    return pd.DataFrame(records, columns=["timestamp", "ticker", "mid", "market_bid", "market_ask"])


def generate_rfqs(market: pd.DataFrame, count=60, seed=43, sizes=(10, 25, 50)) -> list[RFQ]:
    if count < 0 or not sizes or any(type(x) is not int or x <= 0 for x in sizes):
        raise ValueError("invalid RFQ count or sizes")
    if market.empty and count:
        raise ValueError("cannot sample RFQs from empty market")
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(market), size=count, replace=True)
    requests = [RFQ(market.iloc[int(i)].timestamp, str(market.iloc[int(i)].ticker), int(rng.choice(sizes))) for i in indices]
    return sorted(requests, key=lambda r: (r.timestamp, r.ticker))


class MarketEnvironment:
    def __init__(self, market: pd.DataFrame, requests: list[RFQ]):
        required = {"timestamp", "ticker", "mid", "market_bid", "market_ask"}
        if not required.issubset(market.columns) or market.duplicated(["timestamp", "ticker"]).any():
            raise ValueError("market needs unique (timestamp, ticker) rows and price columns")
        if not market.empty and (not np.isfinite(market[["mid", "market_bid", "market_ask"]].to_numpy(dtype=float)).all() or
                                 ((market["mid"] <= 0) | (market["market_bid"] <= 0) |
                                  (market["market_bid"] > market["mid"]) |
                                  (market["mid"] > market["market_ask"])).any()):
            raise ValueError("invalid market prices")
        self.market = market.copy()
        self.requests = sorted(requests, key=lambda r: (r.timestamp, r.ticker))
        self._prices = {(row.timestamp, row.ticker): float(row.mid) for row in self.market.itertuples()}
        if any((r.timestamp, r.ticker) not in self._prices for r in self.requests):
            raise ValueError("request lacks a matching market price")

    def mid_for(self, request: RFQ) -> float:
        return self._prices[(request.timestamp, request.ticker)]

    def latest_marks(self) -> dict[str, float]:
        latest = self.market.sort_values("timestamp").groupby("ticker").tail(1)
        return dict(zip(latest.ticker, latest.mid))


def run_simulation(environment: MarketEnvironment, maker: MarketMaker,
                   client: ClientModel) -> dict[str, object]:
    refusals = risk_rejections = 0
    for request in environment.requests:
        quote = maker.quote(request.ticker, request.quantity, environment.mid_for(request), request.timestamp)
        maker.add_quoted_trade(quote)
        response = client.show(quote)
        if response.hf_action == "refuse":
            refusals += 1
            continue
        action = "sell" if response.hf_action == "buy" else "buy"
        trade = CompletedTrade(quote.ticker, quote.trade_volume, float(response.trade_price),
                               action, quote.ref_price, quote.bid_price, quote.offer_price, quote.date)
        try:
            maker.add_trade(trade)
        except ValueError as exc:
            if str(exc) != "inventory limit exceeded":
                raise
            risk_rejections += 1
    marks = environment.latest_marks()
    return {"quotes": len(maker.quoted_trades), "trades": len(maker.completed_trades),
            "client_refusals": refusals, "risk_rejections": risk_rejections,
            "marks": marks, "valuation": maker.mark_to_market(marks)}
