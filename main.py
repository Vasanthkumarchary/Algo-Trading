import logging
import logging.config
from pathlib import Path

import yaml

from engine.data_loader import load_csv
from engine.sma_trend_strategy import SMATrendStrategy
from backtest.engine import BacktestEngine
from backtest.metrics import compute_equity_curve, compute_max_drawdown


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

    strategy = SMATrendStrategy(window=200)

    engine = BacktestEngine(
        data=data,
        strategy=strategy,
        initial_capital=100000,
        risk_per_trade=0.01,
        max_drawdown=0.20,
        atr_period=14,
        atr_multiplier=2.0,
        transaction_cost=10.0,
        slippage=0.5,
    )

    trades = engine.run()

    equity_df = compute_equity_curve(trades, initial_capital=100000)
    max_dd = compute_max_drawdown(equity_df["equity"])

    logger.info("ATR-based baseline completed")
    logger.info("Final equity: %.2f", equity_df["equity"].iloc[-1])
    logger.info("Max drawdown observed: %.2f", max_dd)
    logger.info("Total trades: %d", len(trades))


if __name__ == "__main__":
    main()
