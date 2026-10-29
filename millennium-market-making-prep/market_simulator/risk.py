"""Basic position and return risk metrics."""
import numpy as np
import pandas as pd


def exposure(positions: dict[str, int], marks: dict[str, float]) -> dict[str, float]:
    return {ticker: quantity * marks[ticker] for ticker, quantity in positions.items()}


def historical_volatility(prices: pd.Series, periods_per_year: int = 252) -> float:
    if periods_per_year <= 0 or (prices <= 0).any():
        raise ValueError("prices and annualization must be positive")
    returns = prices.pct_change().dropna()
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year)) if len(returns) >= 2 else float("nan")


def beta(asset_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    paired = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    if len(paired) < 2 or paired.iloc[:, 1].var() == 0:
        raise ValueError("need at least two aligned returns and nonzero benchmark variance")
    return float(paired.iloc[:, 0].cov(paired.iloc[:, 1]) / paired.iloc[:, 1].var())
