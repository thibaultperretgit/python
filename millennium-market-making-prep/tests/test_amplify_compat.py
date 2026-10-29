import pandas as pd
import pytest

from AmplifyArbitrageTrading import HedgeFund as ArbitrageHedgeFund
from AmplifyQuantTrading import Data, Exchange, HedgeFund as hf, MarketMaker
from market_simulator import CompletedTrade, ExchangeTrade, QuotedTrade


def test_named_data_feeds_match_public_shapes_and_are_copied():
    prices = Data.get_price_series("PricestoFeedserver")
    requests = Data.get_price_requests("PriceRequeststoFeedserver")
    assert prices and all(len(row) == 3 for row in prices)
    assert requests[:2] == [["FB", 0, 3010], ["AAPL", 10_000, 6929]]
    price_lookup = {(ticker, date): price for ticker, date, price in prices}
    assert price_lookup[("FB", 0)] == 194.44
    prices[0][2] = -1
    assert Data.get_price_series("PricestoFeedserver")[0][2] > 0

    wide = Data.get_price_series("PricestoFeedserverEtfUpdate", True)
    assert isinstance(wide, pd.DataFrame)
    assert list(wide.columns) == ["AAPL", "AMZN", "FAANG", "FB", "GOOGL", "NFLX"]
    assert wide.index.name == "date" and len(wide) == 1141


def test_quote_responder_and_market_maker_compatibility_surface():
    hf.reset(seed=7)
    quote = QuotedTrade("AAPL", 10, 100, 98, 102, 0)
    response = hf.show(quote)
    assert response.hf_action in {"buy", "sell", "refuse"}
    assert response.ticker == "AAPL"

    maker = MarketMaker.mm()
    assert set(maker.current_positions) == {"FAANG", "FB", "AAPL", "AMZN", "NFLX", "GOOGL"}
    assert maker.add_quoted_trade(quote)
    trade = CompletedTrade("AAPL", 10, 98, "buy", 100, 98, 102, 0)
    assert maker.add_trade(trade)
    assert maker.current_positions["AAPL"].position_volume == 10

    execution = Exchange.execute(ExchangeTrade("FAANG", 2.5, 100, "sell", 0))
    assert maker.update_ETF_position(execution)
    assert maker.current_positions["FAANG"].position_volume == -2.5
    assert maker.ETF_positions == [execution]


def test_arbitrage_account_tracks_cash_positions_pnl_and_commission():
    prices = pd.DataFrame({"FAANG": [100.0, 105.0]}, index=pd.Index([0, 1], name="date"))
    account = ArbitrageHedgeFund.hf(commission_percentage=0.001, data=prices,
                                    initial_balance=10_000)
    account.execute_order("FAANG", 10, "buy", 0)
    account.execute_order("FAANG", 10, "sell", 1)
    position = account.current_positions["FAANG"]
    assert position.direction == "FLAT" and position.position_volume == 0
    assert position.profit_loss == pytest.approx(50)
    assert position.commission_costs == pytest.approx(2.05)
    assert account.balance == pytest.approx(10_047.95)
    assert [row["action"] for row in position.trade_history] == ["BUY", "SELL"]


@pytest.mark.parametrize("method,name", [
    (Data.get_price_series, "missing-price-feed"),
    (Data.get_price_requests, "missing-request-feed"),
])
def test_unknown_data_feed_is_rejected(method, name):
    with pytest.raises(ValueError, match="unknown"):
        method(name)
