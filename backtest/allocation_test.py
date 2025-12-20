from typing import Tuple

import pandas as pd

from backtest.engine import BacktestEngine
from backtest.metrics import compute_equity_curve, compute_max_drawdown
from engine.sma_trend_strategy import SMATrendStrategy
from engine.mean_reversion_strategy import MeanReversionStrategy


def run_allocation(
    data: pd.DataFrame,
    total_capital: float,
    trend_weight: float,
) -> Tuple[float, float]:
    """
    Run portfolio with static allocation.
    Returns (final_equity, max_drawdown).
    """

    trend_capital = total_capital * trend_weight
    mr_capital = total_capital * (1 - trend_weight)

    # --- Trend ---
    trend_engine = BacktestEngine(
        data=data,
        strategy=SMATrendStrategy(window=200),
        initial_capital=trend_capital,
        risk_per_trade=0.01,
        max_drawdown=0.20,
        atr_period=14,
        atr_multiplier=2.0,
        transaction_cost=10.0,
        slippage=0.5,
    )

    trend_trades = trend_engine.run()
    trend_equity = compute_equity_curve(trend_trades, trend_capital)

    # --- Mean Reversion ---
    mr_engine = BacktestEngine(
        data=data,
        strategy=MeanReversionStrategy(),
        initial_capital=mr_capital,
        risk_per_trade=0.005,
        max_drawdown=0.20,
        atr_period=14,
        atr_multiplier=1.0,
        transaction_cost=10.0,
        slippage=0.5,
    )

    mr_trades = mr_engine.run()
    mr_equity = compute_equity_curve(mr_trades, mr_capital)

    # --- Combine ---
    combined = trend_equity.merge(
        mr_equity,
        on="date",
        how="outer",
        suffixes=("_trend", "_mr"),
    ).sort_values("date").ffill()

    combined["portfolio_equity"] = (
        combined["equity_trend"] + combined["equity_mr"]
    )

    final_equity = combined["portfolio_equity"].iloc[-1]
    max_dd = compute_max_drawdown(combined["portfolio_equity"])

    return final_equity, max_dd
