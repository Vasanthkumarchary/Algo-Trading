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
    with open("config/logging.yaml", "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


def load_config():
    with open("config/execution.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    cfg = load_config()

    data = load_csv(Path(cfg["run"]["data_path"]))
    total_capital = cfg["run"]["capital"]

    equity_curves = {}

    # --- Trend Strategy ---
    if cfg["trend_strategy"]["enabled"]:
        cap = total_capital * cfg["portfolio"]["allocation"]["trend"]

        trend_engine = BacktestEngine(
            data=data,
            strategy=SMATrendStrategy(
                window=cfg["trend_strategy"]["sma_window"]
            ),
            initial_capital=cap,
            risk_per_trade=cfg["trend_strategy"]["risk_per_trade"],
            max_drawdown=cfg["execution"]["max_drawdown"],
            atr_period=cfg["trend_strategy"]["atr_period"],
            atr_multiplier=cfg["trend_strategy"]["atr_multiplier"],
            transaction_cost=cfg["execution"]["transaction_cost"],
            slippage=cfg["execution"]["slippage"],
        )

        trades = trend_engine.run()
        equity_curves["trend"] = compute_equity_curve(trades, cap)

    # --- Mean Reversion Strategy ---
    if cfg["mean_reversion_strategy"]["enabled"]:
        cap = total_capital * cfg["portfolio"]["allocation"]["mean_reversion"]

        mr_engine = BacktestEngine(
            data=data,
            strategy=MeanReversionStrategy(
                mean_window=cfg["mean_reversion_strategy"]["mean_window"],
                regime_window=cfg["mean_reversion_strategy"]["regime_window"],
                atr_period=cfg["mean_reversion_strategy"]["atr_period"],
                entry_atr=cfg["mean_reversion_strategy"]["entry_atr"],
            ),
            initial_capital=cap,
            risk_per_trade=cfg["mean_reversion_strategy"]["risk_per_trade"],
            max_drawdown=cfg["execution"]["max_drawdown"],
            atr_period=cfg["mean_reversion_strategy"]["atr_period"],
            atr_multiplier=cfg["mean_reversion_strategy"]["atr_multiplier"],
            transaction_cost=cfg["execution"]["transaction_cost"],
            slippage=cfg["execution"]["slippage"],
        )

        trades = mr_engine.run()
        equity_curves["mean_reversion"] = compute_equity_curve(trades, cap)

    portfolio = combine_equity_curves(equity_curves)
    dd = compute_max_drawdown(portfolio["portfolio_equity"])

    logger.info("Final portfolio equity: %.2f", portfolio["portfolio_equity"].iloc[-1])
    logger.info("Portfolio max drawdown: %.2f", dd)


if __name__ == "__main__":
    main()
