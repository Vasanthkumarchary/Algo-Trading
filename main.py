import logging
import logging.config
from pathlib import Path

import yaml

from engine.data_loader import load_csv
from engine.mean_reversion_strategy import MeanReversionStrategy
from backtest.engine import BacktestEngine
from backtest.metrics import compute_equity_curve, compute_max_drawdown
from backtest.trade_analysis import analyze_trades


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

    strategy = MeanReversionStrategy(
        mean_window=20,
        regime_window=200,
        atr_period=14,
        entry_atr=1.0,
    )

    engine = BacktestEngine(
        data=data,
        strategy=strategy,
        initial_capital=100000,
        risk_per_trade=0.005,   # lower risk for MR
        max_drawdown=0.20,
        atr_period=14,
        atr_multiplier=1.0,     # tighter stop
        transaction_cost=10.0,
        slippage=0.5,
    )

    trades = engine.run()

    equity_df = compute_equity_curve(trades, initial_capital=100000)
    max_dd = compute_max_drawdown(equity_df["equity"])
    stats = analyze_trades(trades)

    logger.info("Mean Reversion Strategy completed")
    logger.info("Final equity: %.2f", equity_df["equity"].iloc[-1])
    logger.info("Max drawdown: %.2f", max_dd)
    logger.info("Closed trades: %d", stats["total_trades"])
    logger.info("Win rate: %.2f%%", stats["win_rate"] * 100)
    logger.info("Avg win: %.2f", stats["avg_win"])
    logger.info("Avg loss: %.2f", stats["avg_loss"])
    logger.info("Expectancy: %.2f", stats["expectancy"])


if __name__ == "__main__":
    main()
