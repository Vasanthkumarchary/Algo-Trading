import logging
import logging.config
from pathlib import Path

import yaml

from engine.data_loader import load_csv
from backtest.allocation_test import run_allocation


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

    allocations = [
        0.90,
        0.80,
        0.70,
        0.60,
        0.50,
    ]

    logger.info("===== ALLOCATION TUNING RESULTS =====")

    for w in allocations:
        final_eq, max_dd = run_allocation(
            data=data,
            total_capital=total_capital,
            trend_weight=w,
        )

        logger.info(
            "Trend %d%% / MR %d%% | Final equity: %.2f | Max DD: %.2f",
            int(w * 100),
            int((1 - w) * 100),
            final_eq,
            max_dd,
        )


if __name__ == "__main__":
    main()
