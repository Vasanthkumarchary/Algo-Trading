import pandas as pd
from typing import List, Dict

from engine.strategy import Strategy


class BacktestEngine:
    """
    Backtest engine with risk management.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Strategy,
        initial_capital: float,
        risk_per_trade: float,
        max_drawdown: float,
        transaction_cost: float = 0.0,
        slippage: float = 0.0,
    ):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_drawdown = max_drawdown
        self.transaction_cost = transaction_cost
        self.slippage = slippage

        self.position = 0
        self.entry_price = None
        self.position_size = 0

        self.cash = initial_capital
        self.equity_peak = initial_capital
        self.trades: List[Dict] = []

    def _current_drawdown(self):
        return (self.cash - self.equity_peak) / self.equity_peak

    def run(self):
        for i in range(len(self.data)):
            window = self.data.iloc[: i + 1]
            signal = self.strategy.generate_signal(window)

            market_price = window.iloc[-1]["close"]
            date = window.iloc[-1]["date"]

            # Update equity peak
            self.equity_peak = max(self.equity_peak, self.cash)

            # Kill switch
            if self._current_drawdown() <= -self.max_drawdown:
                self.trades.append(
                    {
                        "date": date,
                        "type": "HALT",
                        "reason": "Max drawdown breached",
                        "cash": self.cash,
                    }
                )
                break

            # Entry
            if self.position == 0 and signal.direction == 1:
                risk_amount = self.cash * self.risk_per_trade
                execution_price = market_price + self.slippage

                if execution_price <= 0:
                    continue

                self.position_size = risk_amount / execution_price
                self.entry_price = execution_price
                self.position = 1
                self.cash -= self.transaction_cost

                self.trades.append(
                    {
                        "date": date,
                        "type": "BUY",
                        "price": execution_price,
                        "size": self.position_size,
                        "cash": self.cash,
                    }
                )

            # Exit
            elif self.position == 1 and signal.direction == 0:
                execution_price = market_price - self.slippage
                pnl = (
                    (execution_price - self.entry_price)
                    * self.position_size
                    - self.transaction_cost
                )

                self.cash += pnl
                self.position = 0
                self.entry_price = None
                self.position_size = 0

                self.trades.append(
                    {
                        "date": date,
                        "type": "SELL",
                        "price": execution_price,
                        "pnl": pnl,
                        "cash": self.cash,
                    }
                )

        return self.trades
