import pandas as pd
from typing import List, Dict


def compute_equity_curve(
    trades: List[Dict],
    initial_capital: float,
) -> pd.DataFrame:
    """
    Build equity curve from executed trades.
    Handles the case of zero trades safely.
    """

    # No trades → flat equity
    if not trades:
        return pd.DataFrame(
            {
                "date": [None],
                "equity": [initial_capital],
            }
        )

    equity = initial_capital
    records = []

    for trade in trades:
        if trade["type"] == "SELL":
            equity = trade["cash"]

        records.append(
            {
                "date": trade.get("date"),
                "equity": equity,
            }
        )

    return pd.DataFrame(records)


def compute_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Compute maximum drawdown from equity curve.
    """
    cumulative_max = equity_curve.cummax()
    drawdown = equity_curve - cumulative_max
    return drawdown.min()
