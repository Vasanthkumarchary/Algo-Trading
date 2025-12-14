from engine.strategy import Strategy, Signal
import pandas as pd


class DummyStrategy(Strategy):
    """
    A no-op strategy that always stays flat.
    Used to validate the strategy interface.
    """

    def generate_signal(self, data: pd.DataFrame):
        return Signal(direction=0)
