from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class Signal:
    """
    Represents a trading signal.
    direction: +1 (long), -1 (short), 0 (flat)
    """

    def __init__(self, direction: int):
        if direction not in (-1, 0, 1):
            raise ValueError("Signal direction must be -1, 0, or 1")
        self.direction = direction

    def __repr__(self):
        return f"Signal(direction={self.direction})"


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    """

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """
        Given historical data, return a trading signal.
        Must not place trades or manage positions.
        """
        pass
