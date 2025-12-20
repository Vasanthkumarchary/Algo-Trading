import pandas as pd
from typing import List, Dict


def analyze_trades(trades: List[Dict]) -> dict:
    """
    Analyze executed trades.
    Assumes SELL and STOP trades contain PnL.
    """

    pnl_trades = [t for t in trades if t["type"] in ("SELL", "STOP")]

    if not pnl_trades:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "expectancy": 0.0,
            "stop_exits": 0,
            "regime_exits": 0,
        }

    df = pd.DataFrame(pnl_trades)

    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] <= 0]

    win_rate = len(wins) / len(df)
    avg_win = wins["pnl"].mean() if not wins.empty else 0.0
    avg_loss = losses["pnl"].mean() if not losses.empty else 0.0

    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    return {
        "total_trades": len(df),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "stop_exits": (df["type"] == "STOP").sum(),
        "regime_exits": (df["type"] == "SELL").sum(),
    }
