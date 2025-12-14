import logging
import logging.config
from pathlib import Path
import yaml


def setup_logging():
    config_path = Path("config/logging.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    sample_file = Path("data/raw/sample.csv")

    try:
        from engine.data_loader import load_csv

        df = load_csv(sample_file)
        logger.info("Loaded %d rows of data", len(df))
        logger.info("Date range: %s -> %s", df["date"].min(), df["date"].max())
    except Exception as e:
        logger.error("Data loading failed: %s", e)


if __name__ == "__main__":
    main()
