import pandas as pd

from engine.strategy import Strategy, Signal


class SMATrendStrategy(Strategy):
    """
    Trend-following strategy using SMA-200 regime.

    Long when price is above SMA-200.
    Flat when price is below SMA-200.
    """

    def __init__(self, window: int = 200):
        self.window = window

    def generate_signal(self, data: pd.DataFrame):
        # Not enough data to compute SMA
        if len(data) < self.window:
            return Signal(direction=0)

        closes = data["close"]
        sma = closes.rolling(window=self.window).mean().iloc[-1]
        price = closes.iloc[-1]

        if price > sma:
            return Signal(direction=1)

        return Signal(direction=0)
