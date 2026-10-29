"""Inventory, cash, average-cost P&L, quote and execution history."""
from dataclasses import dataclass, field
import math
from .quotes import QuotedTrade, make_quote
from .trades import CompletedTrade


REFERENCE_TICKERS = ("FAANG", "FB", "AAPL", "AMZN", "NFLX", "GOOGL")


@dataclass
class Position:
    position_volume: float = 0  # Signed: long positive, short negative.
    open_price: float = 0.0
    realized_profit_loss: float = 0.0  # Gross of transaction costs.
    ticker: str = ""
    date: object = 0
    commission_costs: float = 0.0
    trade_history: list[dict[str, object]] = field(default_factory=list)

    @property
    def direction(self) -> str:
        return "LONG" if self.position_volume > 0 else "SHORT" if self.position_volume < 0 else "FLAT"

    @property
    def profit_loss(self) -> float:
        return self.realized_profit_loss

    def __repr__(self) -> str:
        return (f"CurrentPosition(ticker={self.ticker}, "
                f"position_volume={self.position_volume:g}, "
                f"open_price={self.open_price:g}, date={self.date})")


class MarketMaker:
    def __init__(self, initial_cash: float = 0.0, inventory_limit: int = 1000,
                 spread_fraction: float = 0.02, skew_strength: float = 0.01,
                 transaction_cost_rate: float = 0.0,
                 tracked_tickers: tuple[str, ...] | list[str] | None = None) -> None:
        if not math.isfinite(initial_cash) or type(inventory_limit) is not int or inventory_limit <= 0:
            raise ValueError("finite cash and positive integer inventory limit required")
        if not 0 < spread_fraction < 2 or not 0 <= skew_strength < 1 or not 0 <= transaction_cost_rate < 1:
            raise ValueError("invalid spread, skew, or cost rate")
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.inventory_limit = inventory_limit
        self.spread_fraction = spread_fraction
        self.skew_strength = skew_strength
        self.transaction_cost_rate = transaction_cost_rate
        if tracked_tickers is not None and (len(set(tracked_tickers)) != len(tracked_tickers)
                                            or any(not ticker for ticker in tracked_tickers)):
            raise ValueError("tracked_tickers must be unique and nonempty")
        self.current_positions: dict[str, Position] = {
            str(ticker): Position(ticker=str(ticker)) for ticker in (tracked_tickers or ())
        }
        self.quoted_trades: list[QuotedTrade] = []
        self.completed_trades: list[CompletedTrade] = []
        self.ETF_positions: list[object] = []
        self.transaction_costs = 0.0

    def position(self, ticker: str) -> int:
        return self.current_positions.get(ticker, Position()).position_volume

    def quote(self, ticker: str, volume: int, mid: float, date: object) -> QuotedTrade:
        skew = self.skew_strength * self.position(ticker) / self.inventory_limit
        return make_quote(ticker, volume, mid, date, self.spread_fraction, skew)

    def add_quoted_trade(self, quote: QuotedTrade) -> str:
        self.quoted_trades.append(quote)
        return "Quoted trade added successfully"

    def _book_fill(self, ticker: str, volume: float, price: float, action: str,
                   date: object) -> None:
        delta = volume if action.lower() == "buy" else -volume
        old = self.current_positions.get(ticker, Position(ticker=ticker))
        new_quantity = old.position_volume + delta
        if abs(new_quantity) > self.inventory_limit:
            raise ValueError("inventory limit exceeded")
        fee = volume * price * self.transaction_cost_rate
        if old.position_volume == 0 or old.position_volume * delta > 0:
            new_avg = (abs(old.position_volume) * old.open_price + abs(delta) * price) / abs(new_quantity)
            realized = old.realized_profit_loss
        else:
            closed = min(abs(old.position_volume), abs(delta))
            realized = old.realized_profit_loss + closed * (price - old.open_price) * (1 if old.position_volume > 0 else -1)
            new_avg = 0.0 if new_quantity == 0 else (price if old.position_volume * new_quantity < 0 else old.open_price)
        history = list(old.trade_history)
        history.append({"action": action.upper(), "price": price, "volume": volume,
                        "commission": fee, "date": date})
        self.cash -= delta * price + fee
        self.transaction_costs += fee
        self.current_positions[ticker] = Position(
            position_volume=new_quantity,
            open_price=new_avg,
            realized_profit_loss=realized,
            ticker=ticker,
            date=date,
            commission_costs=old.commission_costs + fee,
            trade_history=history,
        )

    def add_trade(self, trade: CompletedTrade) -> str:
        """Execute atomically; rejected limit breaches do not change state."""
        self._book_fill(trade.ticker, trade.trade_volume, trade.trade_price,
                        trade.mm_action, trade.date)
        self.completed_trades.append(trade)
        return "Completed trade added successfully"

    def update_ETF_position(self, executed_trade) -> str:
        """Log an exchange fill separately while updating the same position ledger."""
        required = ("ticker", "trade_volume", "trade_price", "action", "date")
        if not all(hasattr(executed_trade, field) for field in required):
            raise TypeError("executed_trade lacks required fields")
        action = str(executed_trade.action).lower()
        volume = float(executed_trade.trade_volume)
        price = float(executed_trade.trade_price)
        if action not in {"buy", "sell"} or not math.isfinite(volume) or volume <= 0:
            raise ValueError("invalid exchange fill")
        if not math.isfinite(price) or price <= 0:
            raise ValueError("invalid exchange price")
        self._book_fill(str(executed_trade.ticker), volume, price, action,
                        executed_trade.date)
        self.ETF_positions.append(executed_trade)
        return "ETF position updated successfully"

    def mark_to_market(self, marks: dict[str, float]) -> dict[str, float]:
        """Equity = cash + marked inventory; total P&L = equity - initial cash."""
        for ticker, position in self.current_positions.items():
            if position.position_volume and (ticker not in marks or not math.isfinite(marks[ticker]) or marks[ticker] <= 0):
                raise ValueError(f"missing or invalid mark for {ticker}")
        inventory_value = sum(p.position_volume * marks[t] for t, p in self.current_positions.items() if p.position_volume)
        realized = sum(p.realized_profit_loss for p in self.current_positions.values())
        unrealized = sum(p.position_volume * (marks[t] - p.open_price) for t, p in self.current_positions.items() if p.position_volume)
        equity = self.cash + inventory_value
        return {"cash": self.cash, "inventory_value": inventory_value, "equity": equity,
                "realized_pnl": realized, "unrealized_pnl": unrealized,
                "transaction_costs": self.transaction_costs, "total_pnl": equity - self.initial_cash}

    @classmethod
    def mm(cls, **kwargs):
        """Compatibility factory with pre-created public-notebook positions."""
        kwargs.setdefault("inventory_limit", 10**12)
        kwargs.setdefault("tracked_tickers", REFERENCE_TICKERS)
        return cls(**kwargs)
