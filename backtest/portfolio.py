import pandas as pd
from typing import Dict


def combine_equity_curves(curves: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combine multiple equity curves into a portfolio curve.
    Assumes each curve has columns: date, equity
    """

    merged = None

    for name, df in curves.items():
        df = df.copy()
        df = df.rename(columns={"equity": f"equity_{name}"})

        if merged is None:
            merged = df
        else:
            merged = pd.merge(
                merged,
                df,
                on="date",
                how="outer",
            )

    merged = merged.sort_values("date").ffill()

    equity_cols = [c for c in merged.columns if c.startswith("equity_")]
    merged["portfolio_equity"] = merged[equity_cols].sum(axis=1)

    return merged
