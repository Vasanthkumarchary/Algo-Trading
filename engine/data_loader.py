import pandas as pd
from pathlib import Path


REQUIRED_COLUMNS = {"date", "open", "high", "low", "close", "volume"}


def load_csv(file_path: Path) -> pd.DataFrame:
    """
    Load market data from a CSV file with basic validation.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    df = pd.read_csv(file_path)

    # Normalize column names
    df.columns = [c.lower().strip() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="raise")

    # Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    return df
