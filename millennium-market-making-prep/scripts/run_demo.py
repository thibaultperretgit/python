from market_simulator import (ClientModel, MarketEnvironment, MarketMaker,
                              generate_market_data, generate_rfqs, run_simulation)

market = generate_market_data(seed=42)
requests = generate_rfqs(market, seed=43)
report = run_simulation(MarketEnvironment(market, requests),
                        MarketMaker(initial_cash=100_000, inventory_limit=100),
                        ClientModel(seed=44))
print(report)
