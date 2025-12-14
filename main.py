import logging
import logging.config
from pathlib import Path

import yaml

from engine.data_loader import load_csv
from engine.buy_and_hold import BuyAndHoldStrategy
from backtest.engine import BacktestEngine
from backtest.metrics import compute_equity_curve, compute_max_drawdown


def setup_logging():
    """
    Configure logging from YAML configuration.
    """
    config_path = Path("config/logging.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load data
    data = load_csv(Path("data/raw/sample.csv"))
    logger.info("Loaded %d rows of data", len(data))

    # Strategy
    strategy = BuyAndHoldStrategy()

    # Backtest with realism
    engine = BacktestEngine(
        data=data,
        strategy=strategy,
        initial_capital=100000,
        transaction_cost=10.0,   # flat cost per trade
        slippage=0.5,            # price slippage
    )

    trades = engine.run()

    # Metrics
    equity_df = compute_equity_curve(trades, initial_capital=100000)
    max_dd = compute_max_drawdown(equity_df["equity"])

    logger.info("Backtest completed")
    logger.info("Final equity: %.2f", equity_df["equity"].iloc[-1])
    logger.info("Max drawdown: %.2f", max_dd)

    for trade in trades:
        logger.info(trade)


if __name__ == "__main__":
    main()
