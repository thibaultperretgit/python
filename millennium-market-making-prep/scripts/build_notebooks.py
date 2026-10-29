"""Build ten tutorial notebooks from the Codex tutorial notebook scaffold."""
from pathlib import Path
import json
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = Path('/Users/thibaultperret/.codex/skills/jupyter-notebook/scripts/new_notebook.py')


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": source.splitlines(True)}


SETUP = """from pathlib import Path
import market_simulator
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from market_simulator import (MarketMaker, ClientModel, MarketEnvironment,
    QuotedTrade, CompletedTrade, generate_market_data, generate_rfqs, run_simulation, make_quote)
from market_simulator.risk import beta, historical_volatility

# Resolve synthetic data from the installed local package, independent of kernel CWD.
DATA = Path(market_simulator.__file__).resolve().parents[1] / 'data'
prices = pd.read_csv(DATA / 'market_prices.csv', parse_dates=['timestamp'])
requests = pd.read_csv(DATA / 'client_rfqs.csv', parse_dates=['timestamp'])
print(prices.head(2).to_string(index=False))
"""

# Each task has a prompt, a starter signature, a completed implementation, and a public check.
COURSE = [
    ("01", "Python and Market Data Fundamentals", "Lists, dictionaries, DataFrames, time series, and validation", [
        ("Sample requests", "Return the first n records as dictionaries in original order. For n <= 0, return an empty list. Example: [{'ticker':'A'}, {'ticker':'B'}], 1 -> [{'ticker':'A'}].",
         "def sample_requests(records: list[dict], n: int) -> list[dict]:\n    # TODO\n    raise NotImplementedError",
         "def sample_requests(records: list[dict], n: int) -> list[dict]:\n    return records[:max(0, n)]",
         "assert sample_requests([{'ticker':'A'}, {'ticker':'B'}], 1) == [{'ticker':'A'}]\nassert sample_requests([], 10) == []",
         "O(min(n, len(records))) time and space for the slice. A loop also works; remember that assignment does not copy a list."),
        ("Validate market data", "Return True only if required columns timestamp, ticker, mid exist, every mid is finite and positive, and (timestamp,ticker) keys are unique. Empty rows are allowed if columns exist.",
         "def valid_market(frame: pd.DataFrame) -> bool:\n    # TODO\n    raise NotImplementedError",
         "def valid_market(frame: pd.DataFrame) -> bool:\n    required = {'timestamp', 'ticker', 'mid'}\n    return (required.issubset(frame.columns) and frame['mid'].notna().all()\n            and np.isfinite(frame['mid']).all() and (frame['mid'] > 0).all()\n            and frame['ticker'].notna().all() and frame['timestamp'].notna().all()\n            and not frame.duplicated(['timestamp', 'ticker']).any())",
         "assert valid_market(prices)\nassert not valid_market(pd.DataFrame({'timestamp':[1,1], 'ticker':['A','A'], 'mid':[1,2]}))",
         "O(n) time and O(n) temporary space in pandas. Check columns before indexing; duplicate keys make joins ambiguous."),
        ("Group and return", "For one ticker, sort by timestamp and return a Series of simple returns (P_t/P_(t-1)-1), excluding the first missing value. Example prices 100, 110 -> [0.10].",
         "def ticker_returns(frame: pd.DataFrame, ticker: str) -> pd.Series:\n    # TODO\n    raise NotImplementedError",
         "def ticker_returns(frame: pd.DataFrame, ticker: str) -> pd.Series:\n    series = frame.loc[frame['ticker'] == ticker].sort_values('timestamp')['mid']\n    return series.pct_change().dropna()",
         "assert np.isclose(ticker_returns(pd.DataFrame({'ticker':['A','A'], 'timestamp':[1,2], 'mid':[100,110]}), 'A').iloc[0], .1)\nassert ticker_returns(prices, 'MISSING').empty",
         "O(n log n) from sorting; filtering is O(n). Avoid computing returns before sorting by time."),
    ]),
    ("02", "Market Making Fundamentals", "Bid/ask, RFQs, side conventions, inventory and cash", [
        ("Two-sided price", "Given a positive mid and full spread fraction, return (bid, ask). Example 100 and 0.02 -> (99,101). Reject invalid inputs.",
         "def two_sided(mid: float, spread: float) -> tuple[float, float]:\n    # TODO\n    raise NotImplementedError",
         "def two_sided(mid: float, spread: float) -> tuple[float, float]:\n    if not np.isfinite(mid) or mid <= 0 or not np.isfinite(spread) or not 0 < spread < 2:\n        raise ValueError('invalid mid or spread')\n    return (mid * (1 - spread/2), mid * (1 + spread/2))",
         "assert two_sided(100, .02) == (99, 101)",
         "O(1) time and space. The spread fraction here is full spread; 2% on each side would require 0.04."),
        ("Join RFQs to prices", "Return an RFQ DataFrame enriched with `mid`, matching timestamp and ticker. Preserve all RFQs. Raise ValueError if any match is missing or duplicated.",
         "def enrich_rfqs(rfqs: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:\n    # TODO\n    raise NotImplementedError",
         "def enrich_rfqs(rfqs: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:\n    if market.duplicated(['timestamp', 'ticker']).any():\n        raise ValueError('duplicate price key')\n    result = rfqs.merge(market[['timestamp','ticker','mid']], on=['timestamp','ticker'], how='left', validate='many_to_one')\n    if result['mid'].isna().any():\n        raise ValueError('missing price')\n    return result",
         "joined = enrich_rfqs(requests, prices)\nassert len(joined) == len(requests) and joined.mid.notna().all()",
         "Hash join is typically O(n+m) expected time and O(n+m) space. A nested scan is much slower."),
        ("Maker cash update", "Return (new_inventory, new_cash). A maker buy of q at p adds q shares and spends qp; a maker sell subtracts q shares and receives qp. Fee rate is applied to notional on either side.",
         "def apply_fill(inventory: int, cash: float, side: str, q: int, p: float, fee_rate: float = 0.0) -> tuple[int, float]:\n    # TODO\n    raise NotImplementedError",
         "def apply_fill(inventory: int, cash: float, side: str, q: int, p: float, fee_rate: float = 0.0) -> tuple[int, float]:\n    if side not in {'buy','sell'} or type(q) is not int or q <= 0 or p <= 0 or not 0 <= fee_rate < 1:\n        raise ValueError('invalid fill')\n    delta = q if side == 'buy' else -q\n    return inventory + delta, cash - delta*p - q*p*fee_rate",
         "assert apply_fill(0, 1000, 'buy', 2, 100) == (2, 800)\nassert apply_fill(0, 1000, 'sell', 2, 100) == (-2, 1200)",
         "O(1) time and space. Do not confuse client direction with maker direction."),
    ]),
    ("03", "Object-Oriented Market Making", "Quote and trade objects, state management, histories", [
        ("Quote objects", "Build a quote with `make_quote` for ticker ALFA, quantity 10, mid 100, timestamp 0 and full spread 0.02. Return its bid and offer as a tuple.",
         "def object_quote() -> tuple[float, float]:\n    # TODO\n    raise NotImplementedError",
         "def object_quote() -> tuple[float, float]:\n    q = make_quote('ALFA', 10, 100, 0, .02)\n    return q.bid_price, q.offer_price",
         "assert object_quote() == (99,101)",
         "O(1). QuotedTrade is immutable; record a new quote if prices change."),
        ("Execute a maker buy", "Create a MarketMaker with cash 1000 and limit 20. Add a 10-share quote at bid 99, ask 101, then execute a maker buy at the bid. Return (inventory, cash, history_length).",
         "def buy_example() -> tuple[int, float, int]:\n    # TODO\n    raise NotImplementedError",
         "def buy_example() -> tuple[int, float, int]:\n    mm = MarketMaker(initial_cash=1000, inventory_limit=20)\n    q = make_quote('ALFA', 10, 100, 0)\n    mm.add_quoted_trade(q)\n    mm.add_trade(CompletedTrade('ALFA', 10, q.bid_price, 'buy', 100, q.bid_price, q.offer_price, 0))\n    return mm.position('ALFA'), mm.cash, len(mm.completed_trades)",
         "assert buy_example() == (10, 10, 1)",
         "O(1) per trade. A maker buy is a client sell; storing both quote and completed trade preserves the audit trail."),
        ("Mark inventory", "Given a maker that already traded and a current mark dictionary, return its total P&L using mark_to_market.",
         "def total_pnl(maker: MarketMaker, marks: dict[str, float]) -> float:\n    # TODO\n    raise NotImplementedError",
         "def total_pnl(maker: MarketMaker, marks: dict[str, float]) -> float:\n    return maker.mark_to_market(marks)['total_pnl']",
         "m = MarketMaker(initial_cash=1000)\nq = make_quote('A', 1, 100, 0)\nm.add_trade(CompletedTrade('A', 1, 99, 'buy', 100, 99, 101, 0))\nassert total_pnl(m, {'A':100}) == 1",
         "O(k) for k open tickers. Equity equals cash plus marked inventory; do not count the purchase price twice."),
    ]),
    ("04", "Quantitative Analysis and Risk", "Returns, volatility, beta, exposure, skew, visualization", [
        ("Annualized volatility", "Compute sample standard deviation of simple returns times sqrt(252). Require at least three positive prices. Example constant prices -> 0.",
         "def annualized_vol(prices_series: pd.Series) -> float:\n    # TODO\n    raise NotImplementedError",
         "def annualized_vol(prices_series: pd.Series) -> float:\n    if len(prices_series) < 3 or prices_series.isna().any() or (prices_series <= 0).any():\n        raise ValueError('need at least three positive prices')\n    return float(prices_series.pct_change().dropna().std(ddof=1) * np.sqrt(252))",
         "assert annualized_vol(pd.Series([100,100,100])) == 0",
         "O(n) time; O(n) temporary space. State whether volatility is per day or per simulation step."),
        ("Dollar exposure", "Return signed dollar exposure per ticker given signed positions and positive marks. Example {'A':-2}, {'A':100} -> {'A':-200}.",
         "def dollar_exposure(positions: dict[str, int], marks: dict[str, float]) -> dict[str, float]:\n    # TODO\n    raise NotImplementedError",
         "def dollar_exposure(positions: dict[str, int], marks: dict[str, float]) -> dict[str, float]:\n    return {t: q * marks[t] for t, q in positions.items()}",
         "assert dollar_exposure({'A':-2}, {'A':100}) == {'A':-200}",
         "O(k) time and space. Preserve the sign; absolute exposure answers a different question."),
        ("Inventory skew", "Return (bid,ask) using `maker.quote`; a long position should move both sides below an otherwise identical flat quote. Explain why.",
         "def skewed_prices(maker: MarketMaker, ticker: str, mid: float) -> tuple[float, float]:\n    # TODO\n    raise NotImplementedError",
         "def skewed_prices(maker: MarketMaker, ticker: str, mid: float) -> tuple[float, float]:\n    q = maker.quote(ticker, 1, mid, 0)\n    return q.bid_price, q.offer_price",
         "m = MarketMaker(inventory_limit=10)\nflat = skewed_prices(m, 'A', 100)\nm.add_trade(CompletedTrade('A', 5, 99, 'buy', 100, 99, 101, 0))\nassert skewed_prices(m, 'A', 100)[0] < flat[0]",
         "O(1). A lower ask encourages a client buy, reducing maker inventory; a lower bid discourages further accumulation."),
    ]),
    ("05", "Original Two-Hour Mock Assessment", "120 minutes: validation, joins, quotes, accounting, risk", [
        ("Part 1 — Validate (15 min)", "Return a clean copy of a market DataFrame with columns timestamp,ticker,mid. Remove rows with missing keys or nonpositive/nonfinite mid; keep the latest row for duplicate (timestamp,ticker) keys. Never mutate input. Example duplicate key -> one retained row.",
         "def clean_market(frame: pd.DataFrame) -> pd.DataFrame:\n    # TODO\n    raise NotImplementedError",
         "def clean_market(frame: pd.DataFrame) -> pd.DataFrame:\n    required = {'timestamp','ticker','mid'}\n    if not required.issubset(frame.columns):\n        raise ValueError('missing columns')\n    result = frame.copy()\n    result = result.dropna(subset=['timestamp','ticker','mid'])\n    result = result.loc[np.isfinite(result['mid']) & (result['mid'] > 0)]\n    return result.drop_duplicates(['timestamp','ticker'], keep='last').reset_index(drop=True)",
         "d = pd.DataFrame({'timestamp':[1,1,2], 'ticker':['A','A','B'], 'mid':[100,101,-2]})\nassert clean_market(d).mid.tolist() == [101]",
         "O(n) expected time and space. Copy before filtering; keep-last is intentional."),
        ("Part 2 — Match requests (20 min)", "For each RFQ (timestamp,ticker,quantity), attach the matching mid from cleaned market. Preserve request order; raise ValueError on missing prices or nonpositive quantities. Return DataFrame with original columns plus mid.",
         "def match_requests(rfqs: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:\n    # TODO\n    raise NotImplementedError",
         "def match_requests(rfqs: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:\n    if (rfqs['quantity'] <= 0).any() or rfqs['quantity'].isna().any():\n        raise ValueError('invalid quantity')\n    if market.duplicated(['timestamp','ticker']).any():\n        raise ValueError('ambiguous market key')\n    result = rfqs.merge(market[['timestamp','ticker','mid']], on=['timestamp','ticker'], how='left', sort=False, validate='many_to_one')\n    if result['mid'].isna().any():\n        raise ValueError('missing price')\n    return result",
         "assert len(match_requests(requests.head(2), clean_market(prices))) == 2",
         "O(n+m) expected for a hash join. Many-to-one validation catches duplicate market keys."),
        ("Part 3 — Quote (25 min)", "For a positive mid and signed inventory, return (bid,ask). Full spread is 2% of mid. Shift center down by 0.5% of mid for every 50 long shares, up for short shares; cap inventory magnitude at 100 for skew. Example mid 100, inventory 0 -> (99,101).",
         "def quote_with_inventory(mid: float, inventory: int) -> tuple[float, float]:\n    # TODO\n    raise NotImplementedError",
         "def quote_with_inventory(mid: float, inventory: int) -> tuple[float, float]:\n    if not np.isfinite(mid) or mid <= 0:\n        raise ValueError('invalid mid')\n    clipped = max(-100, min(100, inventory))\n    center = mid * (1 - .005 * clipped / 50)\n    return center - .01*mid, center + .01*mid",
         "assert quote_with_inventory(100,0) == (99,101)\nassert quote_with_inventory(100,50)[1] < 101",
         "O(1). Skew shifts the quote center, not its width; cap prevents extreme inventory from making prices invalid."),
        ("Part 4 — Apply fills (30 min)", "Process rows with side ('buy' or 'sell' from maker viewpoint), quantity, price. Return (inventory,cash), starting at zero inventory and given initial_cash. Buy spends cash; sell earns cash. Reject invalid rows; do not mutate input.",
         "def replay_fills(fills: pd.DataFrame, initial_cash: float) -> tuple[int, float]:\n    # TODO\n    raise NotImplementedError",
         "def replay_fills(fills: pd.DataFrame, initial_cash: float) -> tuple[int, float]:\n    position, cash = 0, float(initial_cash)\n    for row in fills.itertuples(index=False):\n        if row.side not in {'buy','sell'} or row.quantity <= 0 or row.price <= 0:\n            raise ValueError('invalid fill')\n        delta = row.quantity if row.side == 'buy' else -row.quantity\n        position += delta\n        cash -= delta * row.price\n    return position, cash",
         "f = pd.DataFrame([{'side':'buy','quantity':2,'price':99},{'side':'sell','quantity':1,'price':101}])\nassert replay_fills(f, 1000) == (1,903.0)",
         "O(n) time and O(1) extra space. Cash is not profit while open inventory remains."),
        ("Part 5 — Risk and P&L (15 min)", "Given cash, signed positions and current positive marks, return a dict with `equity`, `net_exposure`, and `gross_exposure`. Equity is cash plus signed marked inventory; gross exposure sums absolute marked inventory. Example cash 1000, A:2 at 100 -> equity 1200, net/gross 200.",
         "def risk_report(cash: float, positions: dict[str, int], marks: dict[str, float]) -> dict[str, float]:\n    # TODO\n    raise NotImplementedError",
         "def risk_report(cash: float, positions: dict[str, int], marks: dict[str, float]) -> dict[str, float]:\n    values = []\n    for ticker, quantity in positions.items():\n        price = marks[ticker]\n        if not np.isfinite(price) or price <= 0:\n            raise ValueError('invalid mark')\n        values.append(quantity * price)\n    net = sum(values)\n    return {'equity': cash + net, 'net_exposure': net, 'gross_exposure': sum(abs(v) for v in values)}",
         "assert risk_report(1000, {'A':2}, {'A':100}) == {'equity':1200,'net_exposure':200,'gross_exposure':200}",
         "O(k) time and O(k) space. Net exposure can cancel while gross remains large."),
        ("Part 6 — Beta hedge (15 min)", "Given aligned asset and benchmark return Series, a signed asset position, and positive current prices, estimate beta = covariance(asset, benchmark)/variance(benchmark). Return signed integer benchmark units to offset the asset's beta-weighted dollar exposure, rounded with `round`. Reject fewer than two aligned returns, zero benchmark variance, or invalid prices. Example beta 2, asset 10 shares at 50, benchmark at 100 -> -10 units.",
         "def beta_hedge_units(asset_returns: pd.Series, benchmark_returns: pd.Series, asset_position: int, asset_price: float, benchmark_price: float) -> int:\n    # TODO\n    raise NotImplementedError",
         "def beta_hedge_units(asset_returns: pd.Series, benchmark_returns: pd.Series, asset_position: int, asset_price: float, benchmark_price: float) -> int:\n    if asset_price <= 0 or benchmark_price <= 0:\n        raise ValueError('invalid price')\n    hedge_beta = beta(asset_returns, benchmark_returns)\n    return round(-asset_position * asset_price * hedge_beta / benchmark_price)",
         "r = pd.Series([.01,-.02,.03])\nassert beta_hedge_units(2*r, r, 10, 50, 100) == -10",
         "O(n) for aligned returns; O(n) temporary space. This beta hedge targets broad co-movement, not idiosyncratic risk or execution costs."),
    ]),
]


def build():
    for number, title, goals, tasks in COURSE:
        for kind in ('exercises', 'solutions'):
            output = ROOT / 'notebooks' / kind / f'{number}_{title.lower().replace(" ", "_").replace("-", "_")}.ipynb'
            subprocess.run([sys.executable, str(SCAFFOLD), '--kind', 'tutorial', '--title', title,
                            '--out', str(output), '--force'], check=True, capture_output=True)
            notebook = json.loads(output.read_text())
            intro = f'# {title}\n\nAudience: Python learners preparing for quant interviews. Prerequisites: basic Python and pandas.\n\nGoals: {goals}.\n\nOutline: setup, short tasks, checks, pitfalls. Run cells from top to bottom. All market data here is synthetic.\n'
            cells = [md(intro), code(SETUP)]
            if number == '04':
                cells += [md('## Visual inspection\nPlot one synthetic price path before calculating risk.'),
                          code("prices.loc[prices.ticker == 'ALFA'].plot(x='timestamp', y='mid', title='Synthetic ALFA mid'); plt.show()")]
            if number == '05':
                cells.insert(1, md('**Timebox: 120 minutes.** This is an original practice assessment. No live or proprietary material is used. Public sample checks are outside this notebook; run `python scripts/check_exercises.py 05` after filling TODOs.'))
            for heading, prompt, starter, solution, check, note in tasks:
                cells.append(md(f'## {heading}\n\n{prompt}\n'))
                cells.append(code(starter if kind == 'exercises' else solution))
                if kind == 'solutions':
                    cells.append(md(f'**Reasoning and complexity:** {note}\n\n**Common mistake:** Forgetting the stated side, time ordering, or validation contract. An explicit loop is often a useful alternative when debugging.'))
                    cells.append(code(check))
            cells.append(md('## Extension\nTry a different random seed or add a transaction fee. Explain how your answer changes.'))
            notebook['cells'] = cells
            for index, cell in enumerate(cells):
                cell['id'] = hashlib.sha1(f'{number}-{kind}-{index}'.encode()).hexdigest()[:12]
            notebook['metadata']['kernelspec'] = {'display_name':'Python 3', 'language':'python', 'name':'python3'}
            output.write_text(json.dumps(notebook, indent=2) + '\n')
            print(output.relative_to(ROOT))


if __name__ == '__main__':
    build()
