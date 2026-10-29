"""Create deterministic synthetic CSV files for notebook exercises."""
from pathlib import Path
from market_simulator import generate_market_data, generate_rfqs
import pandas as pd


def main():
    output = Path(__file__).resolve().parents[1] / "data"
    output.mkdir(exist_ok=True)
    market = generate_market_data(periods=120, seed=2026)
    requests = generate_rfqs(market, count=80, seed=2027)
    market.to_csv(output / "market_prices.csv", index=False)
    pd.DataFrame([{"timestamp": r.timestamp, "ticker": r.ticker, "quantity": r.quantity}
                  for r in requests]).to_csv(output / "client_rfqs.csv", index=False)
    print(f"Wrote synthetic CSVs to {output}")


if __name__ == "__main__":
    main()
