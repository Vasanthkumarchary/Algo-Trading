import pandas as pd


def compute_atr(data: pd.DataFrame, period: int = 14) -> float:
    """
    Compute ATR using simple moving average of True Range.
    Returns the latest ATR value.
    """
    high = data["high"]
    low = data["low"]
    close = data["close"]

    prev_close = close.shift(1)

    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = tr.rolling(window=period).mean()

    return atr.iloc[-1]
