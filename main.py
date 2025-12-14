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
    logger.info("Application started")


if __name__ == "__main__":
    main()
