import pandas as pd

from engine.strategy import Strategy, Signal
from engine.indicators import compute_atr


class MeanReversionStrategy(Strategy):
    """
    Mean reversion strategy for sideways regimes.

    Active only when price is below SMA-200.
    Enters when price deviates below SMA-20 by 1 ATR.
    """

    def __init__(
        self,
        mean_window: int = 20,
        regime_window: int = 200,
        atr_period: int = 14,
        entry_atr: float = 1.0,
    ):
        self.mean_window = mean_window
        self.regime_window = regime_window
        self.atr_period = atr_period
        self.entry_atr = entry_atr

    def generate_signal(self, data: pd.DataFrame):
        # Need enough data for regime + mean + ATR
        min_len = max(self.mean_window, self.regime_window, self.atr_period)
        if len(data) < min_len:
            return Signal(direction=0)

        closes = data["close"]

        sma_regime = closes.rolling(self.regime_window).mean().iloc[-1]
        sma_mean = closes.rolling(self.mean_window).mean().iloc[-1]
        price = closes.iloc[-1]

        # Regime filter: disable during uptrend
        if price > sma_regime:
            return Signal(direction=0)

        atr = compute_atr(data, self.atr_period)
        if pd.isna(atr) or atr <= 0:
            return Signal(direction=0)

        # Mean reversion entry
        if price < sma_mean - (self.entry_atr * atr):
            return Signal(direction=1)

        return Signal(direction=0)
