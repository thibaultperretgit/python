"""Deterministic local stand-ins for the public Amplify data-feed names.

The real assessment data is private.  These generators intentionally reproduce
only the observable shapes and names: list rows are ``[ticker, date, price]``
and request rows are ``[ticker, date, volume]``; ETF data can also be requested
as a wide pandas DataFrame indexed by ``date``.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd


REFERENCE_TICKERS = ("FAANG", "FB", "AAPL", "AMZN", "NFLX", "GOOGL")
COMPONENT_TICKERS = ("AAPL", "FB", "AMZN", "NFLX", "GOOGL")


@lru_cache(maxsize=1)
def _etf_price_frame() -> pd.DataFrame:
    """Return a correlated six-asset panel with the public notebook's shape."""
    dates = np.arange(0, 5_700_001, 5_000, dtype=int)
    rng = np.random.default_rng(20261025)
    market_factor = rng.normal(0.00022, 0.0075, len(dates) - 1)
    starts = {
        "AAPL": 74.70,
        "AMZN": 1953.00,
        "FB": 196.44,
        "GOOGL": 1386.00,
        "NFLX": 381.05,
    }
    loadings = {"AAPL": 0.86, "FB": 1.03, "AMZN": 0.92,
                "NFLX": 0.92, "GOOGL": 1.27}
    idiosyncratic_vol = {"AAPL": 0.0045, "FB": 0.0050, "AMZN": 0.0048,
                         "NFLX": 0.0065, "GOOGL": 0.0058}

    columns: dict[str, np.ndarray] = {}
    for ticker in COMPONENT_TICKERS:
        shocks = (loadings[ticker] * market_factor
                  + rng.normal(0.0, idiosyncratic_vol[ticker], len(market_factor)))
        columns[ticker] = np.r_[starts[ticker], starts[ticker] * np.exp(np.cumsum(shocks))]

    rebased = np.column_stack(
        [100.0 * columns[ticker] / columns[ticker][0] for ticker in COMPONENT_TICKERS]
    )
    synthetic = rebased.mean(axis=1)
    dislocation = np.zeros(len(dates))
    innovations = rng.normal(0.0, 0.34, len(dates) - 1)
    for index, innovation in enumerate(innovations, start=1):
        dislocation[index] = 0.91 * dislocation[index - 1] + innovation
    columns["FAANG"] = np.maximum(1.0, synthetic + dislocation)

    frame = pd.DataFrame(columns, index=pd.Index(dates, name="date"))
    return frame[["AAPL", "AMZN", "FAANG", "FB", "GOOGL", "NFLX"]].round(2)


_FIRST_REQUESTS = (
    ("FB", 0, 3010),
    ("AAPL", 10_000, 6929),
    ("FB", 30_000, 7015),
    ("FB", 70_000, 4910),
    ("AAPL", 105_000, 5783),
    ("AAPL", 110_000, 3280),
    ("FB", 115_000, 2465),
    ("AAPL", 120_000, 656),
    ("FB", 130_000, 1948),
    ("FB", 150_000, 1386),
)


_FIRST_REFERENCE_PRICES = {
    ("FB", 0): 194.44,
    ("AAPL", 10_000): 74.63,
    ("FB", 30_000): 195.75,
    ("FB", 70_000): 193.30,
    ("AAPL", 105_000): 73.13,
    ("AAPL", 110_000): 73.83,
    ("FB", 115_000): 185.76,
    ("AAPL", 120_000): 76.56,
    ("FB", 130_000): 191.32,
    ("FB", 150_000): 195.82,
}


def _as_long_records(frame: pd.DataFrame) -> list[list[object]]:
    records: list[list[object]] = []
    for date, row in frame.iterrows():
        for ticker in frame.columns:
            records.append([str(ticker), int(date), float(row[ticker])])
    return records


@lru_cache(maxsize=1)
def _simple_records() -> tuple[tuple[object, ...], ...]:
    frame = _etf_price_frame().copy()
    for (ticker, date), price in _FIRST_REFERENCE_PRICES.items():
        frame.loc[date, ticker] = price
    return tuple(tuple(row) for row in _as_long_records(frame))


@lru_cache(maxsize=2)
def _generated_requests(extended: bool) -> tuple[tuple[object, ...], ...]:
    rng = np.random.default_rng(2027 if not extended else 2028)
    frame = _etf_price_frame()
    tickers = np.array(COMPONENT_TICKERS)
    count = 90 if not extended else 520
    minimum_date = 155_000 if not extended else 0
    eligible_dates = frame.index[frame.index >= minimum_date].to_numpy()
    dates = np.sort(rng.choice(eligible_dates, size=count, replace=True))
    generated = [
        (str(rng.choice(tickers)), int(date), int(rng.integers(250, 7_501)))
        for date in dates
    ]
    if extended:
        return tuple(generated)
    return tuple(_FIRST_REQUESTS) + tuple(generated)


class Data:
    """Compatibility facade for the observable ``AmplifyQuantTrading.Data`` API."""

    _PRICE_FEEDS = {
        "PricestoFeedserver",
        "PricestoFeedserverExtended",
        "PricestoFeedserverEtfUpdate",
    }
    _REQUEST_FEEDS = {
        "PriceRequeststoFeedserver",
        "PriceRequeststoFeedserverExtended",
    }

    @classmethod
    def get_price_series(cls, name: str, as_dataframe: bool = False):
        if name not in cls._PRICE_FEEDS:
            raise ValueError(f"unknown price feed: {name}")
        frame = _etf_price_frame().copy()
        if as_dataframe:
            return frame
        if name == "PricestoFeedserver":
            return [list(row) for row in _simple_records()]
        return _as_long_records(frame)

    @classmethod
    def get_price_requests(cls, name: str) -> list[list[object]]:
        if name not in cls._REQUEST_FEEDS:
            raise ValueError(f"unknown request feed: {name}")
        extended = name == "PriceRequeststoFeedserverExtended"
        return [list(row) for row in _generated_requests(extended)]
