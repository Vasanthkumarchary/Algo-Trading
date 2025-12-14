import pandas as pd
from typing import List, Dict

from engine.strategy import Strategy
from engine.indicators import compute_atr


class BacktestEngine:
    """
    Backtest engine with ATR-based risk management.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Strategy,
        initial_capital: float,
        risk_per_trade: float,
        max_drawdown: float,
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        transaction_cost: float = 0.0,
        slippage: float = 0.0,
    ):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_drawdown = max_drawdown
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.transaction_cost = transaction_cost
        self.slippage = slippage

        self.position = 0
        self.entry_price = None
        self.stop_price = None
        self.position_size = 0.0

        self.cash = initial_capital
        self.equity_peak = initial_capital
        self.trades: List[Dict] = []

    def _current_drawdown(self):
        return (self.cash - self.equity_peak) / self.equity_peak

    def run(self):
        for i in range(len(self.data)):
            window = self.data.iloc[: i + 1]
            signal = self.strategy.generate_signal(window)

            price = window.iloc[-1]["close"]
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

            # Exit on stop-loss
            if self.position == 1 and price <= self.stop_price:
                pnl = (
                    (price - self.entry_price)
                    * self.position_size
                    - self.transaction_cost
                )
                self.cash += pnl

                self.trades.append(
                    {
                        "date": date,
                        "type": "STOP",
                        "price": price,
                        "pnl": pnl,
                        "cash": self.cash,
                    }
                )

                self.position = 0
                self.entry_price = None
                self.stop_price = None
                self.position_size = 0.0
                continue

            # Entry
            if self.position == 0 and signal.direction == 1:
                atr = compute_atr(window, period=self.atr_period)

                if pd.isna(atr) or atr <= 0:
                    continue

                stop_distance = self.atr_multiplier * atr
                risk_amount = self.cash * self.risk_per_trade
                position_size = risk_amount / stop_distance

                execution_price = price + self.slippage
                stop_price = execution_price - stop_distance

                self.position = 1
                self.entry_price = execution_price
                self.stop_price = stop_price
                self.position_size = position_size
                self.cash -= self.transaction_cost

                self.trades.append(
                    {
                        "date": date,
                        "type": "BUY",
                        "price": execution_price,
                        "size": position_size,
                        "stop": stop_price,
                        "cash": self.cash,
                    }
                )

            # Exit on regime break
            elif self.position == 1 and signal.direction == 0:
                execution_price = price - self.slippage
                pnl = (
                    (execution_price - self.entry_price)
                    * self.position_size
                    - self.transaction_cost
                )

                self.cash += pnl

                self.trades.append(
                    {
                        "date": date,
                        "type": "SELL",
                        "price": execution_price,
                        "pnl": pnl,
                        "cash": self.cash,
                    }
                )

                self.position = 0
                self.entry_price = None
                self.stop_price = None
                self.position_size = 0.0

        return self.trades
