import logging
import logging.config
from pathlib import Path

import yaml

from engine.data_loader import load_csv
from engine.dummy_strategy import DummyStrategy


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

    sample_file = Path("data/raw/sample.csv")

    try:
        # Load market data
        df = load_csv(sample_file)
        logger.info("Loaded %d rows of data", len(df))
        logger.info(
            "Date range: %s -> %s",
            df["date"].min(),
            df["date"].max(),
        )

        # Initialize strategy
        strategy = DummyStrategy()

        # Generate signal
        signal = strategy.generate_signal(df)
        logger.info("Generated signal: %s", signal)

    except Exception as e:
        logger.exception("Application failed")


if __name__ == "__main__":
    main()
