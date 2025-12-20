from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionSignal:
    date: str
    strategy: str
    action: str            # BUY / SELL / HOLD
    instrument: str
    quantity: float
    price: Optional[float]
    stop_loss: Optional[float]
    reason: str
