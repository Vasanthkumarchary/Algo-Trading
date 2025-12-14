import pandas as pd
from typing import List, Dict

from engine.strategy import Strategy


class BacktestEngine:
    """
    Minimal backtest engine with realism guards.
    - One instrument
    - One position at a time
    - Long or flat only
    - Transaction costs
    - Slippage
    """

    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Strategy,
        initial_capital: float,
        transaction_cost: float = 0.0,
        slippage: float = 0.0,
    ):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage

        self.position = 0          # 0 = flat, 1 = long
        self.entry_price = None

        self.cash = initial_capital
        self.trades: List[Dict] = []

    def run(self):
        """
        Run backtest bar by bar.
        """

        for i in range(len(self.data)):
            window = self.data.iloc[: i + 1]
            signal = self.strategy.generate_signal(window)

            market_price = window.iloc[-1]["close"]
            date = window.iloc[-1]["date"]

            # Entry
            if self.position == 0 and signal.direction == 1:
                execution_price = market_price + self.slippage
                self.position = 1
                self.entry_price = execution_price
                self.cash -= self.transaction_cost

                self.trades.append(
                    {
                        "date": date,
                        "type": "BUY",
                        "price": execution_price,
                        "cost": self.transaction_cost,
                        "cash": self.cash,
                    }
                )

            # Exit
            elif self.position == 1 and signal.direction == 0:
                execution_price = market_price - self.slippage
                pnl = execution_price - self.entry_price - self.transaction_cost
                self.cash += pnl
                self.position = 0
                self.entry_price = None

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
