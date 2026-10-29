"""Build the unsolved 112-cell public-style quant assessment notebook."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "exercises" / "Quant Assessment.ipynb"
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

    # 0-4: orientation and setup
    add_md("""# Quant Market-Making Assessment — Local Practice Replica

This is an **independent, unsolved practice assessment** modeled only on the public structure of the Millennium/Amplify notebook. It is not a current or proprietary assessment. The feeds are deterministic synthetic data and the simulator is local.

Work from top to bottom. Fill each `TODO`, keep the requested names and signatures, and restart the kernel before a final run. The notebook deliberately contains **112 cells**, matching the public reference notebook's length and four-part progression.""")
    add_md("""## Rules and suggested pacing

- Use ordinary Python, pandas, NumPy, and matplotlib.
- Do not change simulator source while timing an attempt.
- Treat client actions from the client's perspective; completed-trade actions are from the market maker's perspective.
- Suggested practice window: 150 minutes, followed by a separate review pass.
- Public checks give structural feedback only; they are not hidden grading logic.""")
    add_code("""from pathlib import Path
import sys

# Jupyter may start in the repository root, this notebook's directory, or its parent.
_candidates = []
for _base in (Path.cwd(), *Path.cwd().parents):
    _candidates.extend((_base, _base / 'millennium-market-making-prep'))
PROJECT_ROOT = next((path for path in _candidates
                     if (path / 'AmplifyQuantTrading').is_dir()), None)
if PROJECT_ROOT is None:
    raise ModuleNotFoundError('Could not locate millennium-market-making-prep; start Jupyter from the Python workspace')
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from AmplifyQuantTrading import Data, Exchange, MarketMaker, HedgeFund as hf
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

hf.reset(seed=2026)
pd.set_option('display.max_columns', 10)
print('Local assessment environment ready')""")
    add_code("""# Re-run this cell whenever you want deterministic client responses.
hf.reset(seed=2026)
TICKERS = ['AAPL', 'FB', 'AMZN', 'NFLX', 'GOOGL']
ETF_TICKER = 'FAANG'""")
    add_md("""# Challenge 1 — Two-sided price making

Build a small market-making workflow: sample requests, match reference prices, create quote objects, send quotes to a simulated client, and update a market maker's inventory. A neutral quote must place its bid 2% below and its offer 2% above the reference price.""")

    # 5-12: Task A
    add_code("""prices = Data.get_price_series('PricestoFeedserver')
price_requests = Data.get_price_requests('PriceRequeststoFeedserver')
print(f'{len(prices):,} price rows; {len(price_requests):,} requests')
print('First request:', price_requests[0])""")
    add_md("""## Task A — Create a ten-request sample

Iterate over `price_requests` and append exactly the first ten rows to `test_requests`. Preserve order and row shape: `[ticker, date, volume]`.""")
    add_code("test_requests = []")
    add_code("""# TODO: append the first ten requests without modifying price_requests.
raise NotImplementedError('Task A')""")
    add_md("""### Task A output check

Display the result. You should have ten list rows ordered by date.""")
    add_code("print(test_requests)")
    add_md("""### Local structural check

The cell below reports whether the required outer shape is present. It does not reveal or grade your implementation.""")
    add_code("""ok = (len(test_requests) == 10 and all(isinstance(row, list) and len(row) == 3 for row in test_requests))
print('Task A shape:', 'OK' if ok else 'needs work')""")

    # 13-19: Task B
    add_md("""## Task B — Match requests to reference prices

For every sampled request, find the row in `prices` with the same ticker and date. Build `request_with_prices` as `(request, reference_price)` tuples. Preserve sample order and reject missing or duplicate matches explicitly.""")
    add_code("request_with_prices = []")
    add_code("""# TODO: match by both ticker and date, then populate request_with_prices.
# Target shape: [(['AAPL', 10000, 1000], 74.63), ...]
raise NotImplementedError('Task B')""")
    add_md("""### Task B output check

Inspect each pair and verify that the first element is the original three-item request and the second is a positive number.""")
    add_code("""for item in request_with_prices:
    print(item)""")
    add_md("""### Matching check

All ten requests should be matched once. A correct key uses both ticker and date; matching only the ticker is insufficient.""")
    add_code("""shape_ok = (len(request_with_prices) == len(test_requests)
            and all(isinstance(item, tuple) and len(item) == 2 for item in request_with_prices))
print('Task B shape:', 'OK' if shape_ok else 'needs work')""")

    # 20-28: Task C
    add_md("""## Task C — Define `QuotedTrade`

Create a class with attributes `ticker`, `trade_volume`, `ref_price`, `bid_price`, `offer_price`, and `date`. Add readable `__str__` and `__repr__` methods so logs are useful.""")
    add_code("""class QuotedTrade:
    def __init__(self, ticker, trade_volume, ref_price, bid_price, offer_price, date):
        # TODO: assign all six attributes and validate obvious invalid values.
        raise NotImplementedError('Task C class')

    def __str__(self):
        # TODO: return a concise human-readable description.
        raise NotImplementedError('Task C __str__')

    def __repr__(self):
        # TODO: return a constructor-like representation.
        raise NotImplementedError('Task C __repr__')""")
    add_md("""### Quote rule

For this challenge, `SPREAD = 0.02` means **2% away on each side**, not a 2% full width: `bid = ref × 0.98`, `offer = ref × 1.02`.""")
    add_code("quoted_trades = []")
    add_code("""SPREAD = 0.02

# TODO: create one QuotedTrade per matched request and append it.
raise NotImplementedError('Task C quotes')""")
    add_md("""### Task C output check

Print the quote objects. Confirm `bid_price < ref_price < offer_price` for every row.""")
    add_code("print(quoted_trades)")
    add_md("""### Quote shape check

The next cell checks only count and required attribute names.""")
    add_code("""required_quote_fields = ('ticker', 'trade_volume', 'ref_price', 'bid_price', 'offer_price', 'date')
quotes_ok = (len(quoted_trades) == len(request_with_prices)
             and all(all(hasattr(q, field) for field in required_quote_fields) for q in quoted_trades))
print('Task C shape:', 'OK' if quotes_ok else 'needs work')""")

    # 29-35: Task D
    add_md("""## Task D — Ask the hedge-fund client

Call `hf.show(quote)` once for each quote and store each returned `HfResponse` in `hf_responses`. Its `hf_action` is lower-case `buy`, `sell`, or `refuse`, from the client's viewpoint.""")
    add_code("hf_responses = []")
    add_code("""# TODO: submit every quote exactly once and preserve response order.
raise NotImplementedError('Task D')""")
    add_md("""### Task D output check

Inspect the simulated decisions. Accepted client buys execute at your offer; accepted client sells execute at your bid.""")
    add_code("print(hf_responses)")
    add_md("""### Response shape check

Refusals have `trade_price=None`; accepted responses have a positive execution price.""")
    add_code("""valid_actions = {'buy', 'sell', 'refuse'}
responses_ok = (len(hf_responses) == len(quoted_trades)
                and all(r.hf_action in valid_actions for r in hf_responses))
print('Task D shape:', 'OK' if responses_ok else 'needs work')""")

    # 36-41: Tasks E/F
    add_md("""## Task E — Initialize the market maker

`MarketMaker.mm()` creates zero positions for the five stocks and the FAANG ETF. It also exposes `quoted_trades`, `completed_trades`, `ETF_positions`, and `current_positions`.""")
    add_code("""mm = MarketMaker.mm()
print(mm.current_positions)""")
    add_md("""## Task F — Log every quote

Pass every object in `quoted_trades` to `mm.add_quoted_trade`. Logging all quotes is part of the audit trail, whether the client later accepts or refuses.""")
    add_code("""# TODO: log each quote exactly once.
raise NotImplementedError('Task F')""")
    add_md("""### Quote-log check

The log order should equal the submission order.""")
    add_code("print(mm.quoted_trades)")

    # 42-49: Task G/H
    add_md("""## Task G — Define `CompletedTrade`

Create a record with attributes `ticker`, `trade_volume`, `trade_price`, `mm_action`, `ref_price`, `bid_price`, `offer_price`, and `date`. The action is from the **market maker's** viewpoint.""")
    add_code("""class CompletedTrade:
    def __init__(self, ticker, trade_volume, trade_price, mm_action,
                 ref_price, bid_price, offer_price, date):
        # TODO: assign and validate all eight fields.
        raise NotImplementedError('Task G')""")
    add_md("""## Task H — Record accepted trades and update inventory

Ignore refusals. If the client buys, the maker sells; if the client sells, the maker buys. Create a `CompletedTrade` with that opposite action and pass it to `mm.add_trade`.""")
    add_code("""# TODO: translate accepted responses into maker-side completed trades.
raise NotImplementedError('Task H')""")
    add_md("""### Completed-trade output check

Inspect the execution log and current signed positions. Positive inventory is long; negative inventory is short.""")
    add_code("""print(mm.completed_trades)
print(mm.current_positions)""")
    add_md("""### Accounting check

Every completed trade should correspond to one non-refused response, while every submitted quote should remain in the quote log.""")
    add_code("""accepted_count = sum(r.hf_action != 'refuse' for r in hf_responses)
log_ok = len(mm.quoted_trades) == len(quoted_trades) and len(mm.completed_trades) == accepted_count
print('Task H logs:', 'OK' if log_ok else 'needs work')""")

    # 50-61: Challenge 1 visualization
    add_md("""## Task I — Visualize one ticker's accepted quotes

For AAPL completed trades, collect dates, bids, and offers. Keep the three lists aligned.""")
    add_code("""bid_data = []
offer_data = []
quote_dates = []

# TODO: populate the three lists from mm.completed_trades.
raise NotImplementedError('Task I accepted quotes')""")
    add_md("""### Accepted-quote data check

The three lists must have equal lengths and matching order.""")
    add_code("""print('bid_data:', bid_data)
print('offer_data:', offer_data)
print('quote_dates:', quote_dates)""")
    add_md("""### Collect matching reference prices

Build `ref_data` for the same accepted AAPL dates. Avoid accidentally including refused AAPL quotes.""")
    add_code("""ref_data = []

# TODO: populate ref_data in exactly the same order as quote_dates.
raise NotImplementedError('Task I references')""")
    add_md("""### Reference-price check

Confirm all four plotting vectors have equal length before plotting.""")
    add_code("""print('ref_data:', ref_data)
print('lengths:', len(quote_dates), len(bid_data), len(offer_data), len(ref_data))""")
    add_md("""### Plot the three price series

Use a labelled line plot with date on the x-axis and price on the y-axis. The reference line should sit between bid and offer for neutral quotes.""")
    add_code("""# TODO: plot bid_data, ref_data, and offer_data against quote_dates.
raise NotImplementedError('Task I plot')""")
    add_md("""### Challenge 1 checkpoint

Before moving on, restart and run cells 0–59 with your implementations. Check that the logs contain no duplicate quotes or executions.""")
    add_code("""print('quotes:', len(mm.quoted_trades), 'completed:', len(mm.completed_trades))
print('nonzero positions:', {t: p.position_volume for t, p in mm.current_positions.items() if p.position_volume})""")

    # 62-74: Challenge 2
    add_md("""# Challenge 2 — Inventory-aware price skewing

Process an extended request stream. A long stock position should shift both quote sides downward to encourage a client buy and discourage another client sell. A short position should shift both sides upward.""")
    add_md("""## Skewing contract

Choose and document a deterministic rule for long, short, and flat positions. Keep `bid < offer`, keep both prices positive, and do not use future requests or prices. The public reference used piecewise shifts; your implementation may be cleaner but must follow the same economic direction.""")
    add_code("""# Re-importing is harmless and makes the section boundary explicit.
from AmplifyQuantTrading import Data, MarketMaker, HedgeFund as hf
hf.reset(seed=2027)""")
    add_code("""# Reset response state for a reproducible timed attempt.
hf.reset(seed=2027)""")
    add_md("""## Reuse your record classes

Challenge 2 uses the `QuotedTrade` and `CompletedTrade` definitions you wrote above. If you run this section alone, execute those class cells first.""")
    add_code("""required_classes_ready = all(name in globals() for name in ('QuotedTrade', 'CompletedTrade'))
print('Record classes ready:', required_classes_ready)""")
    add_md("""## Task A — Full request loop

For each request: locate the matching price, inspect current inventory, calculate a skewed two-sided quote, log it, ask the client, and record any accepted trade with the opposite maker action. Track AAPL inventory over time for later inspection.""")
    add_code("""mm = MarketMaker.mm()
prices = Data.get_price_series('PricestoFeedserverExtended')
price_requests = Data.get_price_requests('PriceRequeststoFeedserverExtended')
print(len(prices), len(price_requests))""")
    add_code("print(mm.current_positions)")
    add_code("""aapl_positions = []
aapl_position_dates = []

# TODO: implement the sequential inventory-aware quoting loop.
raise NotImplementedError('Challenge 2 Task A')""")
    add_code("""print('quotes logged:', len(mm.quoted_trades))
print('trades completed:', len(mm.completed_trades))
print('final positions:', mm.current_positions)""")
    add_md("""## Task B — Visualize skewed AAPL quotes

Extract AAPL date, bid, reference, and offer series from `mm.quoted_trades`. Plot them together and explain where inventory caused an asymmetric center shift.""")
    add_code("""# TODO: build aligned AAPL series and plot them.
raise NotImplementedError('Challenge 2 Task B')""")
    add_md("""# Research interlude — Beta and hedging

Estimate each component stock's beta to the FAANG ETF using aligned simple returns. These estimates will be inputs to Challenge 3.""")

    # 76-81: beta research
    add_md("""## Beta definition

For stock return series $R_i$ and ETF returns $R_m$, compute

$$\\beta_i = \\frac{\\operatorname{Cov}(R_i, R_m)}{\\operatorname{Var}(R_m)}.$$

Use one consistent return convention, drop only the initial missing row, and verify that the ETF variance is positive.""")
    add_code("""import pandas as pd
prices_long = Data.get_price_series('PricestoFeedserverEtfUpdate')""")
    add_md("""## Equal-weight ETF construction

The five components can be rebased to 100 at the first date. Their row-wise mean is a synthetic equal-weight basket. The supplied FAANG series is a tradable ETF with temporary deviations from that basket.""")
    add_code("prices_long = Data.get_price_series('PricestoFeedserverEtfUpdate')")
    add_code("""# TODO: reshape prices_long or split it by ticker, sort by date,
# and calculate aligned simple-return Series for all six assets.
raise NotImplementedError('Beta returns')""")
    add_code("""betas = {}

# TODO: calculate each component beta to FAANG and populate betas.
raise NotImplementedError('Beta estimates')""")

    # 82-94: Challenge 3
    add_md("""# Challenge 3 — Beta-adjusted ETF hedging

Extend Challenge 2. After every accepted stock trade, calculate its beta-weighted dollar exposure and execute an opposing FAANG hedge through the local exchange.""")
    add_md("""## Hedging tools and sign convention

Create `ExchangeTrade(ticker, trade_volume, ref_price, action, date)`. `Exchange.execute` returns an executed trade; `mm.update_ETF_position` records it. A maker stock buy creates positive exposure and therefore needs an ETF sell. A maker stock sell needs an ETF buy.""")
    add_code("""mm = MarketMaker.mm()
prices = Data.get_price_series('PricestoFeedserverEtfUpdate', True)
price_requests = Data.get_price_requests('PriceRequeststoFeedserverExtended')
hf.reset(seed=2028)""")
    add_code("""class ExchangeTrade:
    def __init__(self, ticker, trade_volume, ref_price, action, date):
        # TODO: assign and validate the five exchange-order fields.
        raise NotImplementedError('Challenge 3 ExchangeTrade')""")
    add_code("print(prices.head())")
    add_code("""net_exposure = []
etf_position_history = []
exposure_dates = []

# TODO: run the quote/response loop, execute one beta hedge after each fill,
# and record beta-adjusted net exposure after every request.
raise NotImplementedError('Challenge 3 Task A')""")
    add_code("""hedge_log_ok = len(mm.ETF_positions) <= len(mm.completed_trades)
print('Hedge log structurally plausible:', hedge_log_ok)
print('Final positions:', mm.current_positions)""")
    add_md("""## Task B — Plot beta-adjusted net exposure

Plot `net_exposure` against `exposure_dates`, add a horizontal zero line, axis labels, and a title. Discuss large residual jumps rather than assuming the hedge is perfect.""")
    add_code("""# TODO: plot beta-adjusted net exposure through time.
raise NotImplementedError('Challenge 3 net-exposure plot')""")
    add_code("""# TODO: plot FAANG position units through time.
raise NotImplementedError('Challenge 3 ETF-position plot')""")
    add_md("""### Risk interpretation

Beta hedging targets common-factor sensitivity, not spread risk, idiosyncratic moves, discrete-share rounding, execution costs, or model error.""")
    add_code("""# TODO: calculate and print mean absolute and maximum absolute net exposure.
raise NotImplementedError('Challenge 3 risk summary')""")
    add_md("""### Challenge 3 reflection

Write three short observations: when exposure is largest, whether hedge direction is correct, and which modeling assumption most limits the result.""")

    # 95-103: arbitrage research
    add_md("""# Research interlude — Real versus synthetic ETF

Construct the equal-weight synthetic basket and study `real FAANG − synthetic FAANG`. A stationary-looking spread may indicate relative-value opportunities, but visual convergence alone is not proof of arbitrage.""")
    add_md("""## Research task

Split the long price records into six aligned series, rebase each component to 100, average the five rebased components, and calculate the real-minus-synthetic spread. Summarize its distribution and inspect it through time.""")
    add_code("prices_long = Data.get_price_series('PricestoFeedserverEtfUpdate')")
    add_code("""# TODO: create aligned AAPL, FB, AMZN, NFLX, GOOGL, and FAANG Series.
raise NotImplementedError('Arbitrage research reshape')""")
    add_code("""# TODO: build synthetic_faang and spread = real_faang - synthetic_faang.
raise NotImplementedError('Arbitrage research spread')""")
    add_code("""# TODO: print descriptive spread statistics and note possible outliers.
raise NotImplementedError('Arbitrage research summary')""")
    add_md("""## Research visualization

Use one figure for real versus synthetic prices and another for the spread. Include labels, legends, and a zero line on the spread chart.""")
    add_code("""# TODO: plot real_faang and synthetic_faang together.
raise NotImplementedError('Arbitrage comparison plot')""")
    add_code("""# TODO: plot the spread with a horizontal zero line.
raise NotImplementedError('Arbitrage spread plot')""")

    # 104-111: Challenge 4
    add_md("""# Challenge 4 — ETF/component arbitrage

Build a stateful relative-value strategy using the commission-aware hedge-fund account. Open a six-leg position only when the expected edge exceeds round-trip costs, avoid stacking uncontrolled positions, and close all legs when the spread converges or at the final date.""")
    add_code("""from AmplifyQuantTrading import Data
from AmplifyArbitrageTrading import HedgeFund as ArbitrageHedgeFund

prices = Data.get_price_series('PricestoFeedserverEtfUpdate', True)""")
    add_code("""hedge_fund = ArbitrageHedgeFund.hf(
    commission_percentage=0.001,
    data=prices,
)""")
    add_code("print(prices.head())")
    add_code("""# TODO: implement entry, sizing, state tracking, exit, and final liquidation.
# Use hedge_fund.execute_order(ticker, volume, action, date) for every leg.
raise NotImplementedError('Challenge 4 Task A')""")
    add_code("""# TODO: calculate total realized P&L net of commissions and print ending balance.
raise NotImplementedError('Challenge 4 results')""")
    add_code("""# TODO: choose one ticker and display its trade_history as a DataFrame.
raise NotImplementedError('Challenge 4 audit trail')""")
    add_md("""# Final submission checklist

- Restart the kernel and run every completed cell in order.
- Confirm all TODOs and `NotImplementedError` statements are gone.
- Check quote/trade/hedge logs for duplicates and sign errors.
- Confirm plots have labels and aligned series.
- Explain spread, inventory, beta, and commission conventions in your own words.

Keep this notebook unsolved for fresh timed attempts; make a copy before entering an answer you want to retain.""")

    if len(cells) != 112:
        raise RuntimeError(f"expected 112 cells, built {len(cells)}")
    return cells


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        sys.executable, str(SCAFFOLD), "--kind", "tutorial",
        "--title", "Quant Market-Making Assessment", "--out", str(OUTPUT), "--force",
    ], check=True, capture_output=True)
    notebook = json.loads(OUTPUT.read_text())
    cells = build_cells()
    for index, cell in enumerate(cells):
        cell["id"] = hashlib.sha1(f"quant-assessment-{index}".encode()).hexdigest()[:12]
    notebook["cells"] = cells
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3"
    }
    notebook["metadata"]["assessment"] = {
        "kind": "independent-public-structure-replica",
        "solution_included": False,
        "synthetic_data": True,
    }
    OUTPUT.write_text(json.dumps(notebook, indent=2) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
