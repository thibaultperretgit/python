import math
import pandas as pd
import pytest

from market_simulator import (MarketMaker, ClientModel, QuotedTrade, CompletedTrade,
                              MarketEnvironment, generate_market_data, generate_rfqs,
                              run_simulation, make_quote)
from market_simulator.risk import beta, historical_volatility


def trade(q, side):
    return CompletedTrade(q.ticker, q.trade_volume, q.bid_price if side == "buy" else q.offer_price,
                          side, q.ref_price, q.bid_price, q.offer_price, q.date)


def test_quote_and_client_competitiveness():
    q = make_quote("ALFA", 10, 100, 0)
    assert q.bid_price == pytest.approx(99)
    assert q.offer_price == pytest.approx(101)
    client = ClientModel(seed=1)
    cheaper = make_quote("ALFA", 10, 100, 0, skew_fraction=0.005)
    assert client.acceptance_probability(cheaper, "buy") > client.acceptance_probability(q, "buy")
    assert client.acceptance_probability(cheaper, "sell") < client.acceptance_probability(q, "sell")


def test_cash_inventory_and_realized_unrealized_pnl():
    mm = MarketMaker(initial_cash=10000, transaction_cost_rate=0.001)
    q = make_quote("ALFA", 10, 100, 0)
    mm.add_trade(trade(q, "buy"))
    assert mm.position("ALFA") == 10
    assert mm.cash == pytest.approx(10000 - 990 - 0.99)
    assert mm.mark_to_market({"ALFA": 100})["unrealized_pnl"] == pytest.approx(10)
    q2 = make_quote("ALFA", 10, 110, 1)
    mm.add_trade(trade(q2, "sell"))
    v = mm.mark_to_market({})
    assert mm.position("ALFA") == 0
    assert v["realized_pnl"] == pytest.approx(121)  # 111.1 - 99 per share = 12.1
    assert v["total_pnl"] == pytest.approx(v["realized_pnl"] - v["transaction_costs"])
    assert v["unrealized_pnl"] == 0


def test_short_and_flip():
    mm = MarketMaker(inventory_limit=100)
    mm.add_trade(trade(make_quote("A", 10, 100, 0), "sell"))
    mm.add_trade(trade(make_quote("A", 15, 90, 1), "buy"))
    p = mm.current_positions["A"]
    assert (p.position_volume, p.open_price) == (5, 89.1)
    assert p.realized_profit_loss == pytest.approx(119)  # short at 101, buy at 89.1


def test_limit_rejection_is_atomic():
    mm = MarketMaker(inventory_limit=10)
    q = make_quote("A", 11, 100, 0)
    with pytest.raises(ValueError, match="inventory limit"):
        mm.add_trade(trade(q, "buy"))
    assert mm.cash == 0 and mm.completed_trades == [] and mm.current_positions == {}


def test_validation_and_empty_data():
    with pytest.raises(ValueError):
        make_quote("A", 0, 100, 0)
    with pytest.raises(ValueError):
        QuotedTrade("A", 1, 100, 102, 98, 0)
    with pytest.raises(ValueError):
        MarketMaker(inventory_limit=0)
    with pytest.raises(ValueError):
        MarketMaker().quote("A", 1, -1, 0)
    market = generate_market_data(periods=1)
    assert generate_rfqs(market, count=0) == []
    env = MarketEnvironment(market, [])
    assert run_simulation(env, MarketMaker(), ClientModel())["trades"] == 0
    bad = market.copy()
    bad.loc[0, "mid"] = float("nan")
    with pytest.raises(ValueError, match="market prices"):
        MarketEnvironment(bad, [])


def test_reproducible_paths_requests_and_trades():
    a = generate_market_data(seed=77)
    pd.testing.assert_frame_equal(a, generate_market_data(seed=77))
    req = generate_rfqs(a, seed=88)
    assert req == generate_rfqs(a, seed=88)
    env = MarketEnvironment(a, req)
    first = run_simulation(env, MarketMaker(), ClientModel(seed=99))
    second = run_simulation(env, MarketMaker(), ClientModel(seed=99))
    assert first == second
    assert first["quotes"] == first["trades"] + first["client_refusals"] + first["risk_rejections"]


def test_risk_statistics():
    p = pd.Series([100, 101, 99, 102])
    assert historical_volatility(p) > 0
    r = pd.Series([0.01, -0.02, 0.03])
    assert beta(2 * r, r) == pytest.approx(2)
