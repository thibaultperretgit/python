# Public reference analysis

Source inspected: [maurosuetta/Millennium-Quant-Intern-Assessment](https://github.com/maurosuetta/Millennium-Quant-Intern-Assessment), public `main` branch, 25 October 2026. The repository contains a README and one 112-cell notebook (`Quant Assessment.ipynb`). This is one person's public work; it is **not evidence of the current Millennium assessment**.

## Directly observable

- Challenge 1 begins with a small sample of `price_requests`, joins each `[ticker, date, volume]` request to `prices` by ticker and date, and builds `QuotedTrade(ticker, trade_volume, ref_price, bid_price, offer_price, date)`. The stated exercise quote is `0.98 * ref_price` bid and `1.02 * ref_price` offer. The notebook sends these quotes to `hf.show`, logs quotes with `mm.add_quoted_trade`, and converts accepted client actions to opposing market-maker actions in `CompletedTrade` objects before `mm.add_trade`.
- Challenge 2 uses `mm.current_positions` to skew prices, then processes a longer request stream. A long position shifts both bid and offer down; a short position shifts both up. It plots quote histories.
- A research section uses pandas returns, covariance, and variance to estimate stock betas relative to a synthetic/equal-weight FAANG benchmark. Challenge 3 describes an ETF hedge, `ExchangeTrade`, `Exchange.execute`, and `mm.update_ETF_position`.
- Challenge 4 introduces an ETF/component price-dislocation exercise and an `hf.execute_order` interface. Its documentation mentions cash balance, current positions, commissions, and trade history.
- Imports include private `AmplifyQuantTrading` components `Data`, `Exchange`, `MarketMaker`, and `HedgeFund`, plus public pandas and matplotlib. The notebook also includes `nbgrader` metadata and hidden-parameter/grading placeholders; the actual private data and grading logic are absent.

## Inferred or approximated locally

The local `QuotedTrade`, `CompletedTrade`, `MarketMaker.mm()`, `add_quoted_trade`, `add_trade`, and `current_positions` names resemble the visible interface, but this package is independent. The compatibility facades also provide the publicly visible named `Data` feeds, `HedgeFund.show`, `Exchange.execute`, `update_ETF_position`, and the separate commission-aware arbitrage `HedgeFund.hf`/`execute_order` surface. Synthetic correlated price paths, deterministic RFQs, the client acceptance curve, immediate exchange fills, average-cost P&L, inventory skew, limits, and transaction costs are teaching choices. They do not claim to reproduce the private engine. The local course adds exercises on validation, accounting, and testing. Both the short mock and the 112-cell practice assessment are independently authored.

## Cannot be reproduced from the public repository

The proprietary `AmplifyQuantTrading` implementation, original market/request datasets, exact client response logic, exchange fills, hidden grader, score rules, current assessment wording, and current timing are unavailable. This project does not import or implement that package and does not use the notebook's external image assets.

## Conventions in this project

`mm_action='buy'` means the maker buys from the client at the bid: inventory increases and cash decreases. `mm_action='sell'` means the maker sells at the offer: inventory decreases and cash increases. Fees reduce cash. Signed inventory may be short. Realized P&L uses average cost and excludes fees; unrealized P&L marks open inventory at the latest mid; `total_pnl = cash + marked_inventory - initial_cash = realized + unrealized - fees` (up to floating-point rounding). A full quote spread of 2% means bid 99 and ask 101 at mid 100; the reference notebook's “2% away on each side” means a 4% full spread. Set `spread_fraction=0.04` locally to match those displayed prices.
