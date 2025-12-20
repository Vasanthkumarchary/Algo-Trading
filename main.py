import logging
import logging.config
from pathlib import Path

import yaml

from engine.data_loader import load_csv
from engine.sma_trend_strategy import SMATrendStrategy
from engine.mean_reversion_strategy import MeanReversionStrategy
from backtest.engine import BacktestEngine
from backtest.metrics import compute_equity_curve, compute_max_drawdown
from backtest.portfolio import combine_equity_curves


def setup_logging():
    config_path = Path("config/logging.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    data = load_csv(Path("data/raw/nifty_daily.csv"))
    logger.info("Loaded %d rows of NIFTY data", len(data))

    total_capital = 100000

    # --- Strategy #1: Trend ---
    trend_capital = total_capital * 0.70
    trend_strategy = SMATrendStrategy(window=200)

    trend_engine = BacktestEngine(
        data=data,
        strategy=trend_strategy,
        initial_capital=trend_capital,
        risk_per_trade=0.01,
        max_drawdown=0.20,
        atr_period=14,
        atr_multiplier=2.0,
        transaction_cost=10.0,
        slippage=0.5,
    )

    trend_trades = trend_engine.run()
    trend_equity = compute_equity_curve(
        trend_trades, initial_capital=trend_capital
    )

    # --- Strategy #2: Mean Reversion ---
    mr_capital = total_capital * 0.30
    mr_strategy = MeanReversionStrategy(
        mean_window=20,
        regime_window=200,
        atr_period=14,
        entry_atr=1.0,
    )

    mr_engine = BacktestEngine(
        data=data,
        strategy=mr_strategy,
        initial_capital=mr_capital,
        risk_per_trade=0.005,
        max_drawdown=0.20,
        atr_period=14,
        atr_multiplier=1.0,
        transaction_cost=10.0,
        slippage=0.5,
    )

    mr_trades = mr_engine.run()
    mr_equity = compute_equity_curve(
        mr_trades, initial_capital=mr_capital
    )

    # --- Portfolio ---
    portfolio = combine_equity_curves(
        {
            "trend": trend_equity,
            "mean_reversion": mr_equity,
        }
    )

    portfolio_dd = compute_max_drawdown(portfolio["portfolio_equity"])

    logger.info("===== PORTFOLIO RESULTS =====")
    logger.info("Final portfolio equity: %.2f", portfolio["portfolio_equity"].iloc[-1])
    logger.info("Portfolio max drawdown: %.2f", portfolio_dd)

    logger.info(
        "Trend final equity: %.2f | MR final equity: %.2f",
        trend_equity["equity"].iloc[-1],
        mr_equity["equity"].iloc[-1],
    )


if __name__ == "__main__":
    main()
