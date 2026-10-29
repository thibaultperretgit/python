#!/usr/bin/env python3
"""Populate the notebook scaffold with the candidate-facing assessment."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "QRT_data_science.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


def main() -> None:
    notebook = nbf.read(NOTEBOOK, as_version=4)
    notebook["cells"] = [
        md(
            r"""
# QRT-style mock assessment: data-science coding

**Recommended time: 42 minutes**
**Libraries:** Python standard library, NumPy, and pandas
**Deliverable:** complete the three functions and leave the notebook runnable from top to bottom.

This is an original practice problem built from public descriptions of QRT research assessments. It is not an official or leaked QRT question.
"""
        ),
        md(
            r"""
## Scenario

You receive a noisy cross-sectional panel for 30 synthetic assets over 160 business days. `signal_raw` is observed at the end of day $t$ and `next_day_return` is the return from $t$ to $t+1$. Your task is to build a clean, leakage-aware out-of-sample evaluation of the signal.

The file deliberately contains duplicate `(date, asset)` observations, missing signals, and signal outliers. Later `observation_time` values are corrections and should win when deduplicating.

### Required conventions

1. Keep the latest `observation_time` for each `(date, asset)` pair.
2. Impute a missing signal with the same-day, same-sector median. If that is unavailable, use the same-day median.
3. On each date, winsorize the imputed signal at the 5th and 95th empirical percentiles.
4. On each date, compute a population z-score (`ddof=0`) called `signal_z`.
5. Evaluate only dates on or after **2025-06-02**.
6. Each day, take an equal-weight long position in the top `floor(n/5)` assets and an equal-weight short position in the bottom `floor(n/5)` assets. Break signal ties by ascending `asset` before taking the tails.
7. The daily factor return is `mean(long next_day_return) - mean(short next_day_return)`.
8. Rank IC is the Pearson correlation between the within-day average ranks of `signal_z` and `next_day_return`.
"""
        ),
        code(
            """
from pathlib import Path
import math
import numpy as np
import pandas as pd

SEED = 20261028
np.random.seed(SEED)
pd.set_option("display.max_columns", 20)

candidate_paths = [
    Path("data/market_panel.csv"),
    Path("QRT_mock_test/data/market_panel.csv"),
]
DATA_PATH = next((path for path in candidate_paths if path.exists()), None)
if DATA_PATH is None:
    raise FileNotFoundError("Run this notebook from QRT_mock_test/ or its parent directory.")

raw = pd.read_csv(DATA_PATH)
print(f"Loaded {len(raw):,} rows from {DATA_PATH}")
display(raw.head())
"""
        ),
        md(
            r"""
## Task 1 - Clean and standardize the panel

Complete `clean_panel(raw)`. Return one row per `(date, asset)`, sorted by `date` then `asset`, with two new columns:

- `signal_winsor`: the daily winsorized signal;
- `signal_z`: its daily population z-score.

Do not use `next_day_return` while constructing either signal column.
"""
        ),
        code(
            """
def clean_panel(raw: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement the eight conventions stated above that concern cleaning.
    # Return a new DataFrame; do not mutate raw in place.
    return None
"""
        ),
        code(
            """
def report_check(name, check):
    try:
        check()
        print(f"PASS - {name}")
    except Exception as exc:
        print(f"NOT YET - {name}: {type(exc).__name__}: {exc}")


def check_clean_panel():
    result = clean_panel(raw.copy())
    assert isinstance(result, pd.DataFrame), "return a DataFrame"
    assert len(result) == 4_800, "latest-observation deduplication should leave 4,800 rows"
    assert not result.duplicated(["date", "asset"]).any(), "duplicate keys remain"
    assert {"signal_winsor", "signal_z"}.issubset(result.columns), "missing output columns"
    assert result["signal_z"].notna().all(), "signal_z contains missing values"
    by_day = result.groupby("date")["signal_z"]
    assert np.allclose(by_day.mean().to_numpy(), 0.0, atol=1e-10), "daily means are not zero"
    assert np.allclose(by_day.std(ddof=0).to_numpy(), 1.0, atol=1e-10), "daily std is not one"


report_check("clean_panel", check_clean_panel)
"""
        ),
        md(
            r"""
## Task 2 - Build the holdout portfolio and rank IC

Complete `compute_daily_performance(clean, holdout_start)`. Return a DataFrame sorted by date with these columns:

- `date`
- `factor_return`
- `rank_ic`
- `n_assets`
- `n_per_leg`

The implementation should work for any holdout date and for days with a different number of assets.
"""
        ),
        code(
            """
def compute_daily_performance(clean: pd.DataFrame, holdout_start: str) -> pd.DataFrame:
    # TODO: implement the holdout filter, deterministic tails, factor return, and rank IC.
    return None
"""
        ),
        code(
            """
def check_daily_performance():
    clean = clean_panel(raw.copy())
    daily = compute_daily_performance(clean, "2025-06-02")
    assert isinstance(daily, pd.DataFrame), "return a DataFrame"
    expected = {"date", "factor_return", "rank_ic", "n_assets", "n_per_leg"}
    assert expected.issubset(daily.columns), "missing output columns"
    assert daily["date"].is_monotonic_increasing, "dates are not sorted"
    assert (pd.to_datetime(daily["date"]) >= pd.Timestamp("2025-06-02")).all(), "pre-holdout rows remain"
    assert daily[["factor_return", "rank_ic"]].notna().all().all(), "missing metrics"
    assert (daily["n_per_leg"] == (daily["n_assets"] // 5).clip(lower=1)).all(), "wrong leg size"


report_check("compute_daily_performance", check_daily_performance)
"""
        ),
        md(
            r"""
## Task 3 - Summarize performance

Complete `summarize_performance(daily)` and return a dictionary with:

- `n_days`
- `annualized_return` = $252\,\bar r$
- `annualized_volatility` = $\sqrt{252}\,s_r$, with sample standard deviation (`ddof=1`)
- `sharpe_ratio` = annualized return divided by annualized volatility, assuming zero risk-free rate
- `mean_rank_ic`
- `positive_day_rate`
- `max_drawdown`, computed from the compounded equity curve $(1+r_t)$
"""
        ),
        code(
            """
def summarize_performance(daily: pd.DataFrame) -> dict[str, float]:
    # TODO: implement the requested metrics.
    return {}
"""
        ),
        code(
            """
def check_summary():
    clean = clean_panel(raw.copy())
    daily = compute_daily_performance(clean, "2025-06-02")
    summary = summarize_performance(daily)
    expected = {
        "n_days", "annualized_return", "annualized_volatility", "sharpe_ratio",
        "mean_rank_ic", "positive_day_rate", "max_drawdown",
    }
    assert expected == set(summary), "return exactly the requested keys"
    assert all(np.isfinite(float(value)) for value in summary.values()), "non-finite metric"
    assert int(summary["n_days"]) == len(daily), "n_days mismatch"
    assert 0.0 <= summary["positive_day_rate"] <= 1.0, "invalid hit rate"
    assert summary["max_drawdown"] <= 0.0, "drawdown must be non-positive"


report_check("summarize_performance", check_summary)
"""
        ),
        md(
            r"""
## Final run and two-sentence interpretation

When all checks pass, run the cell below. Then replace the prompt after it with exactly two sentences: one on whether the synthetic signal appears useful out of sample, and one caveat about what this backtest does **not** establish.
"""
        ),
        code(
            """
try:
    clean = clean_panel(raw.copy())
    daily = compute_daily_performance(clean, "2025-06-02")
    summary = summarize_performance(daily)
    display(pd.Series(summary, name="holdout_summary").to_frame())
except Exception as exc:
    print(f"Complete Tasks 1-3, then rerun: {type(exc).__name__}: {exc}")
"""
        ),
        md(
            """
**Your two-sentence interpretation:**
TODO.
"""
        ),
        md(
            """
## Submission checklist

- Restart the kernel and run all cells.
- Confirm the three validation lines say `PASS`.
- Keep your code readable and deterministic.
- Do not include the separate answer key in a timed attempt.
"""
        ),
    ]
    notebook["metadata"].setdefault("kernelspec", {})
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3"}
    nbf.write(notebook, NOTEBOOK)
    print(f"Updated {NOTEBOOK}")


if __name__ == "__main__":
    main()
