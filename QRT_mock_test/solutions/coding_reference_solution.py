#!/usr/bin/env python3
"""Reference implementation for the QRT-style data-science exercise."""

from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "asset",
    "sector",
    "observation_time",
    "signal_raw",
    "volatility_20d",
    "volume_z",
    "next_day_return",
}


def clean_panel(raw: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate, impute, winsorize, and cross-sectionally standardize."""
    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    clean = raw.copy()
    clean["date"] = pd.to_datetime(clean["date"])
    clean["observation_time"] = pd.to_datetime(clean["observation_time"])
    clean = clean.sort_values(["date", "asset", "observation_time"], kind="mergesort")
    clean = clean.drop_duplicates(["date", "asset"], keep="last").copy()

    sector_day_median = clean.groupby(["date", "sector"])["signal_raw"].transform("median")
    day_median = clean.groupby("date")["signal_raw"].transform("median")
    clean["signal_raw"] = clean["signal_raw"].fillna(sector_day_median).fillna(day_median)

    lower = clean.groupby("date")["signal_raw"].transform(lambda s: s.quantile(0.05))
    upper = clean.groupby("date")["signal_raw"].transform(lambda s: s.quantile(0.95))
    clean["signal_winsor"] = clean["signal_raw"].clip(lower=lower, upper=upper)

    day_mean = clean.groupby("date")["signal_winsor"].transform("mean")
    day_std = clean.groupby("date")["signal_winsor"].transform(lambda s: s.std(ddof=0))
    clean["signal_z"] = (clean["signal_winsor"] - day_mean) / day_std.replace(0.0, np.nan)
    clean["signal_z"] = clean["signal_z"].fillna(0.0)

    return clean.sort_values(["date", "asset"]).reset_index(drop=True)


def compute_daily_performance(clean: pd.DataFrame, holdout_start: str | pd.Timestamp) -> pd.DataFrame:
    """Compute daily top-minus-bottom return and cross-sectional rank IC."""
    required = {"date", "asset", "signal_z", "next_day_return"}
    missing = required.difference(clean.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    start = pd.Timestamp(holdout_start)
    sample = clean.loc[pd.to_datetime(clean["date"]) >= start].copy()
    rows: list[dict[str, object]] = []

    for date, group in sample.groupby("date", sort=True):
        group = group.sort_values(["signal_z", "asset"], kind="mergesort")
        k = max(1, len(group) // 5)
        short_return = group.head(k)["next_day_return"].mean()
        long_return = group.tail(k)["next_day_return"].mean()
        signal_rank = group["signal_z"].rank(method="average")
        return_rank = group["next_day_return"].rank(method="average")
        rank_ic = signal_rank.corr(return_rank)
        rows.append(
            {
                "date": pd.Timestamp(date),
                "factor_return": long_return - short_return,
                "rank_ic": rank_ic,
                "n_assets": len(group),
                "n_per_leg": k,
            }
        )

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def summarize_performance(daily: pd.DataFrame) -> dict[str, float]:
    """Return a compact set of annualized and diagnostic metrics."""
    returns = daily["factor_return"].astype(float)
    annualized_return = 252.0 * returns.mean()
    annualized_volatility = np.sqrt(252.0) * returns.std(ddof=1)
    sharpe = annualized_return / annualized_volatility if annualized_volatility > 0 else np.nan
    equity = (1.0 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return {
        "n_days": float(len(daily)),
        "annualized_return": float(annualized_return),
        "annualized_volatility": float(annualized_volatility),
        "sharpe_ratio": float(sharpe),
        "mean_rank_ic": float(daily["rank_ic"].mean()),
        "positive_day_rate": float((returns > 0).mean()),
        "max_drawdown": float(drawdown.min()),
    }


def solve(data_path: str | Path, holdout_start: str = "2025-06-02") -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    raw = pd.read_csv(data_path)
    clean = clean_panel(raw)
    daily = compute_daily_performance(clean, holdout_start)
    metrics = summarize_performance(daily)
    return clean, daily, metrics


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    _, _, result = solve(root / "data" / "market_panel.csv")
    for name, value in result.items():
        print(f"{name:24s} {value:.6f}")
