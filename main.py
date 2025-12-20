import logging
import logging.config
from pathlib import Path
from datetime import date

import yaml

from engine.data_loader import load_csv
from engine.sma_trend_strategy import SMATrendStrategy
from engine.mean_reversion_strategy import MeanReversionStrategy
from backtest.engine import BacktestEngine
from backtest.metrics import compute_equity_curve
from backtest.portfolio import combine_equity_curves
from execution.signals import ExecutionSignal
from execution.order_ticket import write_order_ticket


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
    run_date = str(data.iloc[-1]["date"].date())

    signals = []

    # --- Trend Strategy ---
    if cfg["trend_strategy"]["enabled"]:
        engine = BacktestEngine(
            data=data,
            strategy=SMATrendStrategy(cfg["trend_strategy"]["sma_window"]),
            initial_capital=cfg["run"]["capital"] * cfg["portfolio"]["allocation"]["trend"],
            risk_per_trade=cfg["trend_strategy"]["risk_per_trade"],
            max_drawdown=cfg["execution"]["max_drawdown"],
            atr_period=cfg["trend_strategy"]["atr_period"],
            atr_multiplier=cfg["trend_strategy"]["atr_multiplier"],
            transaction_cost=cfg["execution"]["transaction_cost"],
            slippage=cfg["execution"]["slippage"],
        )

        trades = engine.run()
        if trades:
            last = trades[-1]
            if last["type"] in ("BUY", "SELL"):
                signals.append(
                    ExecutionSignal(
                        date=run_date,
                        strategy="Trend",
                        action=last["type"],
                        instrument="NIFTY",
                        quantity=last.get("size", 0),
                        price=last.get("price"),
                        stop_loss=last.get("stop"),
                        reason="SMA-200 regime change",
                    )
                )

    # --- Mean Reversion Strategy ---
    if cfg["mean_reversion_strategy"]["enabled"]:
        engine = BacktestEngine(
            data=data,
            strategy=MeanReversionStrategy(),
            initial_capital=cfg["run"]["capital"] * cfg["portfolio"]["allocation"]["mean_reversion"],
            risk_per_trade=cfg["mean_reversion_strategy"]["risk_per_trade"],
            max_drawdown=cfg["execution"]["max_drawdown"],
            atr_period=cfg["mean_reversion_strategy"]["atr_period"],
            atr_multiplier=cfg["mean_reversion_strategy"]["atr_multiplier"],
            transaction_cost=cfg["execution"]["transaction_cost"],
            slippage=cfg["execution"]["slippage"],
        )

        trades = engine.run()
        if trades:
            last = trades[-1]
            if last["type"] in ("BUY", "SELL"):
                signals.append(
                    ExecutionSignal(
                        date=run_date,
                        strategy="MeanReversion",
                        action=last["type"],
                        instrument="NIFTY",
                        quantity=last.get("size", 0),
                        price=last.get("price"),
                        stop_loss=last.get("stop"),
                        reason="Reversion to SMA-20",
                    )
                )

    # --- Output ---
    if signals:
        logger.info("===== EXECUTION SIGNALS =====")
        for s in signals:
            logger.info(
                "%s | %s | %s %s qty %.2f | stop %.2f | %s",
                s.date,
                s.strategy,
                s.action,
                s.instrument,
                s.quantity,
                s.stop_loss if s.stop_loss else 0.0,
                s.reason,
            )

        write_order_ticket(signals)
        logger.info("Order ticket written to output/order_ticket.csv")
    else:
        logger.info("No execution signals today")


if __name__ == "__main__":
    main()
