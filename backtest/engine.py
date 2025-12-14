import pandas as pd
from typing import List, Dict

from engine.strategy import Strategy, Signal


class BacktestEngine:
    """
    Minimal backtest engine.
    - One instrument
    - One position at a time
    - Long or flat only
    """

    def __init__(self, data: pd.DataFrame, strategy: Strategy, initial_capital: float):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital

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

            price = window.iloc[-1]["close"]
            date = window.iloc[-1]["date"]

            # Entry
            if self.position == 0 and signal.direction == 1:
                self.position = 1
                self.entry_price = price
                self.trades.append(
                    {
                        "date": date,
                        "type": "BUY",
                        "price": price,
                    }
                )

            # Exit
            elif self.position == 1 and signal.direction == 0:
                pnl = price - self.entry_price
                self.cash += pnl
                self.position = 0
                self.entry_price = None

                self.trades.append(
                    {
                        "date": date,
                        "type": "SELL",
                        "price": price,
                        "pnl": pnl,
                        "cash": self.cash,
                    }
                )

        return self.trades
