# Local market-making Python training

An independent, offline-capable course inspired by [one public notebook](https://github.com/maurosuetta/Millennium-Quant-Intern-Assessment). Read [REFERENCE_ANALYSIS.md](REFERENCE_ANALYSIS.md) for observed interfaces and limitations. This project is for learning, not a copy of a live assessment.

The first long practice notebook is [`notebooks/exercises/Quant Assessment.ipynb`](notebooks/exercises/Quant%20Assessment.ipynb). It starts from a 112-cell structure matching the public reference's approximate length and covers two-sided quotes, client responses, inventory skew, beta hedging, and ETF/component arbitrage. The prose, synthetic data, local checks, and implementation are independent.

A separate unsolved variant, [`notebooks/exercises/Quant Assesment2.ipynb`](notebooks/exercises/Quant%20Assesment2.ipynb), has 119 cells and new tasks on data validation, size-sensitive spreads, hard inventory limits, rolling beta, threshold-based hedging, and z-score relative-value trading. It intentionally has no solution notebook.

## Install (Python 3.11+)

```bash
cd millennium-market-making-prep
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_data.py
```

After installation, the notebooks, CSV files, simulator, and tests run without network access. The CSV generator is deterministic; it writes synthetic data only. The local CSVs are already included as examples.


## Learn and check

```bash
jupyter lab
pytest -q
python scripts/run_demo.py
python scripts/check_exercises.py 01
```

Open `notebooks/exercises/01_...ipynb` through `05_...ipynb` in order. Run setup cells and implement each TODO. `check_exercises.py` checks a completed student notebook by number (`01` to `05`) using public examples. It will report unfinished TODOs as failures. Solutions live in `notebooks/solutions/`; try the exercise first, then compare approaches, complexity, and pitfalls. `pytest` checks the simulator and completed solution notebooks without requiring student TODOs to be filled.

For a longer assessment-style attempt, open either long assessment notebook. Neither has a solution notebook by design. Make a copy before filling one if you want to preserve a clean timed version. The setup uses local packages named `AmplifyQuantTrading` and `AmplifyArbitrageTrading` so the visible import and method shapes resemble the public reference; neither package contains proprietary code or data.

For the original two-hour mock, open exercise notebook 05, use only the given signatures and local data, and work for roughly 120 minutes. Suggested split: 15 minutes for data checks, 20 for matching, 25 for quotes, 30 for accounting, 15 for exposure, and 15 for a beta hedge. Its grading script is separate from the notebook. The solution notebook is a study aid after the attempt.

## Simulator example

```python
from market_simulator import *

market = generate_market_data(seed=42)
rfqs = generate_rfqs(market, seed=43)
environment = MarketEnvironment(market, rfqs)
maker = MarketMaker(initial_cash=100_000, inventory_limit=100, spread_fraction=0.02)
report = run_simulation(environment, maker, ClientModel(seed=44))
print(report["valuation"])
```

All random draws use explicit seeds. The code runs RFQs in timestamp order and marks final positions at each ticker's latest generated mid. The model is educational: no order book, latency, hedging fills, or calibrated market microstructure. A 2% `spread_fraction` is the **full** spread (bid 99, ask 101 when mid is 100).

## Amplify-style compatibility API

The original `market_simulator` imports and behavior remain supported. The longer assessment additionally exposes:

```python
from AmplifyQuantTrading import Data, Exchange, MarketMaker, HedgeFund as hf
from AmplifyArbitrageTrading import HedgeFund

prices = Data.get_price_series("PricestoFeedserverEtfUpdate", True)
requests = Data.get_price_requests("PriceRequeststoFeedserverExtended")
mm = MarketMaker.mm()
```

Observable public names and data shapes are reproduced where practical: named feeds, list and DataFrame price formats, pre-created position records, `hf.show`, quote/trade logs, ETF exchange fills, and a commission-aware arbitrage account. Client decisions, fills, price paths, scoring, and all hidden behavior are local approximations.

## Glossary

- **Bid / ask:** Price where the maker buys from / sells to a client.
- **Mid:** Reference price around which a quote is built.
- **RFQ:** Request for a two-sided quote with ticker, time, and quantity.
- **Spread:** Ask minus bid; `spread_fraction` is that amount divided by mid.
- **Inventory:** Signed shares held by the maker; short positions are negative.
- **Skew:** Shifting both quote sides to influence client trading direction.
- **Mark to market:** Valuing open inventory at the current mid.
- **Realized / unrealized P&L:** Profit on closed quantities / on current open quantities.
- **Exposure:** Signed inventory multiplied by market price.
- **Beta:** Covariance with benchmark returns divided by benchmark variance.
