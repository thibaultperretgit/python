"""Build a second independent, unsolved quant assessment notebook."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "exercises" / "Quant Assesment2.ipynb"
SCAFFOLD = Path("/Users/thibaultperret/.codex/skills/jupyter-notebook/scripts/new_notebook.py")


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": source.splitlines(True)}


def build_cells() -> list[dict]:
    cells: list[dict] = []
    add_md = lambda source: cells.append(md(source))
    add_code = lambda source: cells.append(code(source))

    # 0-4: setup
    add_md("""# Quant Assessment 2 — Adaptive Market Making and Relative Value

This is a fresh, unsolved local mock assessment. It uses the same synthetic simulator API as the first assessment but contains different tasks, decision rules, and risk-management objectives. It is not proprietary or evidence of a current employer assessment.""")
    add_md("""## Instructions

- Suggested timebox: **150 minutes**, followed by a review pass.
- Work from top to bottom and preserve requested names.
- Use only information available at or before the current date.
- Client actions are from the client's perspective; completed-trade actions are from the market maker's perspective.
- Restart the kernel before your final run.
- This notebook intentionally contains no solutions.""")
    add_code("""from pathlib import Path
import sys

_candidates = []
for _base in (Path.cwd(), *Path.cwd().parents):
    _candidates.extend((_base, _base / 'millennium-market-making-prep'))
PROJECT_ROOT = next((path for path in _candidates
                     if (path / 'AmplifyQuantTrading').is_dir()), None)
if PROJECT_ROOT is None:
    raise ModuleNotFoundError('Start Jupyter from the Python workspace')
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from AmplifyQuantTrading import Data, Exchange, MarketMaker, HedgeFund as hf
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

hf.reset(seed=3030)
print('Assessment 2 environment ready')""")
    add_code("""STOCKS = ['AAPL', 'FB', 'AMZN', 'NFLX', 'GOOGL']
ETF = 'FAANG'
RANDOM_SEED = 3030
hf.reset(seed=RANDOM_SEED)""")
    add_md("""## Assessment map

1. Build validated market-data and quote objects.
2. Run an adaptive market maker with inventory limits.
3. Estimate rolling risk and rebalance ETF hedges only when necessary.
4. Trade a z-score-based real-versus-synthetic ETF strategy after costs.""")

    # 5-44: Challenge 1
    add_md("""# Challenge 1 — Reliable quote construction

Build a quote workflow that validates data instead of assuming every input is clean.""")
    add_code("""prices = Data.get_price_series('PricestoFeedserver')
price_requests = Data.get_price_requests('PriceRequeststoFeedserver')
print('price rows:', len(prices), 'request rows:', len(price_requests))
print('sample:', prices[:2], price_requests[:2])""")
    add_md("""## Task 1A — Validate row shapes

Write `validate_rows(prices, requests)`. Every price row must contain ticker, date, positive finite price. Every request must contain ticker, date, and positive integer volume. Return `True`; raise `ValueError` with a useful message for invalid input.""")
    add_code("""def validate_rows(prices, requests):
    # TODO
    raise NotImplementedError('Task 1A')""")
    add_md("""### Public check

The check reports only whether the supplied synthetic feeds pass your validator.""")
    add_code("""try:
    valid = validate_rows(prices, price_requests)
    print('Task 1A:', 'OK' if valid is True else 'return True when valid')
except Exception as exc:
    print('Task 1A needs work:', type(exc).__name__, exc)""")
    add_md("""## Task 1B — Construct a unique price lookup

Build `price_lookup` keyed by `(ticker, date)`. Reject duplicate keys rather than silently overwriting them.""")
    add_code("""price_lookup = {}

# TODO
raise NotImplementedError('Task 1B')""")
    add_md("""### Lookup check

The number of dictionary keys should equal the number of price rows.""")
    add_code("""print('lookup rows:', len(price_lookup), 'price rows:', len(prices))""")
    add_md("""## Task 1C — Create a dispersed request sample

Create `sample_requests` containing 12 requests spread across the first 48 request rows rather than simply taking the first 12. Preserve chronological order and do not mutate the feed.""")
    add_code("""sample_requests = []

# TODO
raise NotImplementedError('Task 1C')""")
    add_md("""### Sample check

Confirm the sample length, date order, and number of distinct tickers.""")
    add_code("""sample_dates = [row[1] for row in sample_requests]
print('rows:', len(sample_requests))
print('chronological:', sample_dates == sorted(sample_dates))
print('tickers:', sorted({row[0] for row in sample_requests}))""")
    add_md("""## Task 1D — Enrich requests

Create `enriched_requests` as dictionaries with keys `ticker`, `date`, `volume`, and `ref_price`. Raise on a missing price.""")
    add_code("""enriched_requests = []

# TODO
raise NotImplementedError('Task 1D')""")
    add_md("""### Enrichment check

Every sampled request should produce exactly one enriched record.""")
    add_code("""print('enriched rows:', len(enriched_requests))
print(enriched_requests[:2])""")
    add_md("""## Task 1E — Define `QuoteTicket`

Create a class with attributes `ticker`, `trade_volume`, `ref_price`, `bid_price`, `offer_price`, and `date`. Validate values inside `__init__`. Add readable `__str__` and constructor-like `__repr__` methods.""")
    add_code("""class QuoteTicket:
    def __init__(self, ticker, trade_volume, ref_price, bid_price, offer_price, date):
        # TODO
        raise NotImplementedError('Task 1E')

    def __str__(self):
        # TODO
        raise NotImplementedError('Task 1E __str__')

    def __repr__(self):
        # TODO
        raise NotImplementedError('Task 1E __repr__')""")
    add_md("""## Task 1F — Size-sensitive quote width

Implement `size_adjusted_quote(ref_price, volume)`. Start 1% away on each side. Add another 0.25 percentage points on each side for volume above 3,000 and another 0.25 points above 6,000. Return `(bid, offer)` and validate inputs.""")
    add_code("""def size_adjusted_quote(ref_price, volume):
    # TODO
    raise NotImplementedError('Task 1F')""")
    add_md("""### Quote examples

Print quotes for volumes 1,000, 4,000, and 7,000 at a reference price of 100. Width should increase monotonically.""")
    add_code("""for example_volume in (1000, 4000, 7000):
    try:
        print(example_volume, size_adjusted_quote(100.0, example_volume))
    except Exception as exc:
        print(type(exc).__name__, exc)""")
    add_md("""## Task 1G — Build sample quotes

Create one `QuoteTicket` per enriched request using your size-sensitive rule. Store them in `sample_quotes`.""")
    add_code("""sample_quotes = []

# TODO
raise NotImplementedError('Task 1G')""")
    add_md("""### Quote-log check

All quote fields should be present, and every bid should be below its offer.""")
    add_code("""quote_fields = ('ticker', 'trade_volume', 'ref_price', 'bid_price', 'offer_price', 'date')
quote_shape_ok = all(all(hasattr(q, field) for field in quote_fields) for q in sample_quotes)
quote_order_ok = all(q.bid_price < q.offer_price for q in sample_quotes)
print('shape:', quote_shape_ok, 'price order:', quote_order_ok)""")
    add_md("""## Task 1H — Submit quotes and record responses

Reset the client to seed 3031, submit every sample quote once, and store results in `sample_responses`.""")
    add_code("""hf.reset(seed=3031)
sample_responses = []

# TODO
raise NotImplementedError('Task 1H')""")
    add_md("""### Response summary

Count buys, sells, and refusals without assuming that every action appears.""")
    add_code("""# TODO
raise NotImplementedError('Task 1H summary')""")
    add_md("""## Task 1I — Define an execution record

Create `ExecutionRecord` with the eight fields expected by `MarketMaker.add_trade`: ticker, volume, execution price, maker action, reference, bid, offer, and date. Validate the maker action.""")
    add_code("""class ExecutionRecord:
    def __init__(self, ticker, trade_volume, trade_price, mm_action,
                 ref_price, bid_price, offer_price, date):
        # TODO
        raise NotImplementedError('Task 1I')""")
    add_md("""## Task 1J — Complete the sample workflow

Create a fresh `sample_mm`, log every quote, translate accepted client actions to opposite maker actions, and add completed executions. Refusals must not create executions.""")
    add_code("""sample_mm = MarketMaker.mm()

# TODO
raise NotImplementedError('Task 1J')""")
    add_md("""### Challenge 1 summary

Report quote count, completed count, refusal count, and non-zero inventory.""")
    add_code("""# TODO
raise NotImplementedError('Challenge 1 summary')""")
    add_md("""## Challenge 1 visualization

Plot reference, bid, and offer for the ticker with the most sample quotes. Use a title, labels, legend, and grid.""")
    add_code("""# TODO
raise NotImplementedError('Challenge 1 plot')""")
    add_md("""### Challenge 1 reflection

In two or three sentences, explain why a larger client order should generally receive a wider quote and identify one disadvantage of widening too aggressively.""")
    add_md("""_Write your answer here before continuing._""")

    # 45-60: Challenge 2
    add_md("""# Challenge 2 — Adaptive market making with a hard risk limit

Run the extended request stream. Quote width depends on request size, quote center depends on inventory, and accepted trades that would breach a hard position limit must be rejected by your strategy.""")
    add_code("""mm = MarketMaker.mm()
prices = Data.get_price_series('PricestoFeedserverExtended')
price_requests = Data.get_price_requests('PriceRequeststoFeedserverExtended')
hf.reset(seed=3032)
POSITION_LIMIT = 30_000
print(len(prices), len(price_requests))""")
    add_md("""## Task 2A — Adaptive quote helper

Implement `adaptive_quote(ref_price, volume, position, limit)`. Begin with the size-adjusted width from Challenge 1. Shift the quote center down when long and up when short, proportionally to `position / limit`. Cap the skew so prices remain sensible.""")
    add_code("""def adaptive_quote(ref_price, volume, position, limit):
    # TODO
    raise NotImplementedError('Task 2A')""")
    add_md("""## Task 2B — Stateful request loop

For each request: find its price, inspect inventory, create and log a `QuoteTicket`, ask the client, translate accepted actions, and test the proposed new position against `POSITION_LIMIT`. Log only fills that remain within the limit. Track refusals, risk rejections, AAPL inventory, and quote width.""")
    add_code("""risk_rejections = 0
client_refusals = 0
aapl_dates = []
aapl_inventory = []
aapl_quote_width = []

# TODO
raise NotImplementedError('Task 2B')""")
    add_md("""### Loop summary

Print request, quote, completion, refusal, rejection, and maximum absolute inventory statistics.""")
    add_code("""# TODO
raise NotImplementedError('Task 2B summary')""")
    add_md("""## Task 2C — Plot AAPL inventory

Plot inventory after each AAPL request. Add horizontal lines for zero and both position limits.""")
    add_code("""# TODO
raise NotImplementedError('Task 2C')""")
    add_md("""## Task 2D — Plot AAPL quote width

Plot `offer_price - bid_price` through time. Explain whether changes came from order size, inventory, or both.""")
    add_code("""# TODO
raise NotImplementedError('Task 2D')""")
    add_md("""## Task 2E — Risk-limit validation

Confirm that no final or historical recorded position exceeded the stated limit. Report the number and fraction of requests rejected by risk.""")
    add_code("""# TODO
raise NotImplementedError('Task 2E')""")
    add_md("""### Challenge 2 reflection

Write three observations: whether the limit bound held, how inventory affected quote centers, and how rejected fills affect client service.""")
    add_md("""_Write your answer here before continuing._""")
    add_code("""print('Challenge 2 complete when all preceding checks are meaningful.')""")

    # 61-74: rolling research
    add_md("""# Research — Rolling volatility and rolling beta

Unlike a single full-sample beta, rolling estimates can reveal whether relationships change through time.""")
    add_code("""wide_prices = Data.get_price_series('PricestoFeedserverEtfUpdate', True)
print(wide_prices.head())""")
    add_md("""## Task 3A — Aligned returns

Create `returns` for all six assets using simple percentage returns. Do not forward-fill missing observations.""")
    add_code("""# TODO
raise NotImplementedError('Task 3A')""")
    add_md("""### Return check

Report shape, missing count, and first two rows.""")
    add_code("""# TODO
raise NotImplementedError('Task 3A check')""")
    add_md("""## Task 3B — Rolling annualized volatility

Using a 60-observation window and 252-period annualization, create `rolling_volatility` for the five stocks. Preserve dates and leave early unavailable values as missing.""")
    add_code("""WINDOW = 60

# TODO
raise NotImplementedError('Task 3B')""")
    add_md("""## Task 3C — Rolling beta

For each stock, calculate rolling covariance with FAANG divided by rolling FAANG variance over the same 60-observation window. Store the result in `rolling_betas`.""")
    add_code("""# TODO
raise NotImplementedError('Task 3C')""")
    add_md("""## Task 3D — Visualize rolling beta

Plot all five rolling beta series with a horizontal reference line at 1. Use a readable figure size and legend.""")
    add_code("""# TODO
raise NotImplementedError('Task 3D')""")
    add_md("""## Task 3E — Select operational beta estimates

Create `latest_betas` from the final non-missing value of each rolling beta series. Reject non-finite values.""")
    add_code("""latest_betas = {}

# TODO
raise NotImplementedError('Task 3E')""")
    add_md("""### Rolling-risk reflection

Identify the stock whose beta varied most and explain why using a single constant beta can leave residual hedge risk.""")
    add_md("""_Write your answer here before continuing._""")

    # 75-88: Challenge 3
    add_md("""# Challenge 3 — Threshold-based portfolio hedging

Repeat adaptive market making, but do not hedge every fill. After each request, calculate current beta-adjusted stock exposure. Trade FAANG only when residual exposure exceeds a specified dollar threshold.""")
    add_code("""mm = MarketMaker.mm()
prices = Data.get_price_series('PricestoFeedserverEtfUpdate', True)
price_requests = Data.get_price_requests('PriceRequeststoFeedserverExtended')
hf.reset(seed=3033)
HEDGE_THRESHOLD = 1_000_000.0""")
    add_code("""class ETFOrder:
    def __init__(self, ticker, trade_volume, ref_price, action, date):
        # TODO
        raise NotImplementedError('Challenge 3 ETFOrder')""")
    add_md("""## Task 3F — Hedging loop

Reuse your adaptive quote logic. After every request, calculate stock beta exposure using `latest_betas` and current prices. Compute exposure after including the existing FAANG position. If its absolute value exceeds `HEDGE_THRESHOLD`, trade enough FAANG to bring it toward zero. Record pre-hedge and post-hedge exposure, dates, and ETF position.""")
    add_code("""pre_hedge_exposure = []
post_hedge_exposure = []
hedge_dates = []
etf_positions = []

# TODO
raise NotImplementedError('Task 3F')""")
    add_md("""### Hedge summary

Report requests, completed stock trades, ETF hedge trades, and the fraction of observations above the threshold after hedging.""")
    add_code("""# TODO
raise NotImplementedError('Task 3F summary')""")
    add_md("""## Task 3G — Compare exposure before and after hedging

Plot both series on one chart with horizontal lines at zero and the positive/negative thresholds.""")
    add_code("""# TODO
raise NotImplementedError('Task 3G')""")
    add_md("""## Task 3H — Plot ETF inventory

Plot the signed FAANG position and mark dates when hedge trades occurred.""")
    add_code("""# TODO
raise NotImplementedError('Task 3H')""")
    add_md("""## Task 3I — Risk metrics

Calculate mean absolute exposure, maximum absolute exposure, 95th percentile absolute exposure, and the number of ETF hedge trades.""")
    add_code("""# TODO
raise NotImplementedError('Task 3I')""")
    add_md("""### Challenge 3 reflection

Compare hedging every fill with hedging only after a threshold breach. Discuss transaction count, residual risk, and operational complexity.""")
    add_md("""_Write your answer here before continuing._""")

    # 89-107: Challenge 4
    add_md("""# Challenge 4 — Z-score ETF relative-value strategy

Build a real-versus-synthetic ETF spread, standardize it with rolling statistics, and trade only statistically unusual deviations.""")
    add_code("""components = STOCKS
initial_prices = wide_prices.loc[wide_prices.index[0], components]
weights = {ticker: 20.0 / initial_prices[ticker] for ticker in components}
synthetic = sum(wide_prices[ticker] * weights[ticker] for ticker in components)
real = wide_prices[ETF]
spread = real - synthetic""")
    add_md("""## Task 4A — Rolling z-score

Using a 60-observation rolling window, calculate rolling spread mean, rolling spread standard deviation, and `zscore`. Avoid division by zero and do not use future data.""")
    add_code("""# TODO
raise NotImplementedError('Task 4A')""")
    add_md("""## Task 4B — Visualize the signal

Plot z-score with horizontal lines at +2, -2, and 0. Clearly show the initial region where the rolling signal is unavailable.""")
    add_code("""# TODO
raise NotImplementedError('Task 4B')""")
    add_md("""## Trading rules

- Enter short real/long synthetic when z-score exceeds +2.
- Enter long real/short synthetic when z-score falls below -2.
- Exit when z-score crosses zero.
- Permit at most one open pair.
- Size one pair from a fixed $25,000 real-ETF notional at entry.
- Store exact entry quantities and use them for exit.
- Force liquidation at the final date.
- Do not trade until the rolling z-score is available.""")
    add_code("""from AmplifyArbitrageTrading import HedgeFund as ArbitrageHedgeFund

account = ArbitrageHedgeFund.hf(
    commission_percentage=0.001,
    data=wide_prices,
)
PAIR_NOTIONAL = 25_000.0""")
    add_md("""## Task 4C — Implement the z-score strategy

Implement entry, exact quantity storage, state-aware exit, and final liquidation with `account.execute_order`. Track entry and exit dates plus their z-scores in `strategy_events`.""")
    add_code("""strategy_events = []
open_pair = None

# TODO
raise NotImplementedError('Task 4C')""")
    add_md("""## Task 4D — Net P&L and reconciliation

Calculate gross realized P&L, total commissions, net P&L, and ending balance. Confirm that net P&L equals ending balance minus initial balance after liquidation.""")
    add_code("""# TODO
raise NotImplementedError('Task 4D')""")
    add_md("""## Task 4E — Trade audit

Create a compact DataFrame from `strategy_events`, display one component's transaction history, and confirm every final position is flat.""")
    add_code("""# TODO
raise NotImplementedError('Task 4E')""")
    add_md("""## Task 4F — Strategy diagnostics

Report number of completed pairs, average holding period, win rate by pair, and largest net losing pair. State any assumptions used to assign commissions across pairs.""")
    add_code("""# TODO
raise NotImplementedError('Task 4F')""")
    add_md("""## Optional stress test

Without changing the main results, describe how entries and P&L might change for thresholds of 1.5 and 2.5 or for doubled commissions.""")
    add_code("""# Optional TODO: run parameter sensitivity on a fresh account.
# Keep the main strategy results above unchanged.
pass""")
    add_md("""## Final written assessment

Answer briefly:

1. Which model assumption is least realistic?
2. Where could look-ahead bias enter this notebook?
3. Why can a profitable backtest still be a poor live strategy?
4. Which single additional risk control would you add first?""")
    add_md("""_Write your answers here._""")
    add_md("""# Submission checklist

- Restart the kernel and run all completed cells.
- Remove remaining `NotImplementedError` statements.
- Confirm quote, execution, and hedge logs have no accidental duplicates.
- Confirm all final arbitrage positions are flat.
- Check every plot has labels, title, legend where appropriate, and aligned data.
- Keep explanations concise and specific to your results.""")
    add_code("""# Final structural reminder; this is not a grader.
print('Notebook:', 'Quant Assesment2.ipynb')
print('Seed:', RANDOM_SEED)
print('Complete the checklist above before review.')""")
    add_md("""## End of assessment

Save this completed attempt under a new filename if you want to preserve a clean copy for another timed run.""")
    add_code("""print('Assessment 2 reached its final cell.')""")

    if len(cells) != 119:
        raise RuntimeError(f"expected 119 cells, built {len(cells)}")
    return cells


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        sys.executable, str(SCAFFOLD), "--kind", "experiment",
        "--title", "Quant Assessment 2", "--out", str(OUTPUT), "--force",
    ], check=True, capture_output=True)
    notebook = json.loads(OUTPUT.read_text())
    cells = build_cells()
    for index, cell in enumerate(cells):
        cell["id"] = hashlib.sha1(f"quant-assessment-2-{index}".encode()).hexdigest()[:12]
    notebook["cells"] = cells
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3"
    }
    notebook["metadata"]["assessment"] = {
        "kind": "independent-practice-assessment",
        "variant": 2,
        "solution_included": False,
        "synthetic_data": True,
    }
    OUTPUT.write_text(json.dumps(notebook, indent=2) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
