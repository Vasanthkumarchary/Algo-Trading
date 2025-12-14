from engine.strategy import Strategy, Signal
import pandas as pd


class BuyAndHoldStrategy(Strategy):
    """
    Buys on first bar, holds forever.
    Used to validate backtest mechanics.
    """

    def generate_signal(self, data: pd.DataFrame):
        if len(data) == 1:
            return Signal(direction=1)
        return Signal(direction=1)
