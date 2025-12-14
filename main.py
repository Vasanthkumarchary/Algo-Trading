import logging
import logging.config
from pathlib import Path

import yaml

from engine.data_loader import load_csv
from engine.buy_and_hold import BuyAndHoldStrategy
from backtest.engine import BacktestEngine


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

    # Load sample market data
    data_path = Path("data/raw/sample.csv")
    data = load_csv(data_path)

    logger.info("Loaded %d rows of data", len(data))

    # Initialize strategy
    strategy = BuyAndHoldStrategy()

    # Initialize backtest engine
    engine = BacktestEngine(
        data=data,
        strategy=strategy,
        initial_capital=100000,
    )

    # Run backtest
    trades = engine.run()

    logger.info("Backtest completed")
    logger.info("Number of trades: %d", len(trades))

    for trade in trades:
        logger.info(trade)


if __name__ == "__main__":
    main()
