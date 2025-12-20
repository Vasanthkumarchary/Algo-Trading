import csv
from typing import List
from execution.signals import ExecutionSignal


def write_order_ticket(
    signals: List[ExecutionSignal],
    path: str = "output/order_ticket.csv",
):
    if not signals:
        return

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "date",
                "strategy",
                "action",
                "instrument",
                "quantity",
                "price",
                "stop_loss",
                "reason",
            ]
        )

        for s in signals:
            writer.writerow(
                [
                    s.date,
                    s.strategy,
                    s.action,
                    s.instrument,
                    round(s.quantity, 2),
                    s.price,
                    s.stop_loss,
                    s.reason,
                ]
            )
