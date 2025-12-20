import pandas as pd
from typing import List, Dict


def yearly_performance(trades: List[Dict]) -> pd.DataFrame:
    """
    Aggregate PnL and trade count by year.
    Considers only SELL and STOP exits.
    """

    records = []

    for trade in trades:
        if trade["type"] in ("SELL", "STOP"):
            records.append(
                {
                    "year": trade["date"].year,
                    "pnl": trade["pnl"],
                }
            )

    if not records:
        return pd.DataFrame(columns=["year", "total_pnl", "trade_count"])

    df = pd.DataFrame(records)

    summary = (
        df.groupby("year")
        .agg(
            total_pnl=("pnl", "sum"),
            trade_count=("pnl", "count"),
        )
        .reset_index()
        .sort_values("year")
    )

    return summary
