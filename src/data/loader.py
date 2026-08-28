from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


# Load and validate an OHLCV CSV file
def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")

    df["Date"] = pd.to_datetime(df["Date"])

    dup_mask = df.duplicated(subset="Date", keep="last")
    if dup_mask.any():
        logger.warning("%d duplicate dates found in %s; keeping last occurrence", dup_mask.sum(), path)
    df = df[~dup_mask]

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_before = len(df)
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
    n_dropped = n_before - len(df)
    if n_dropped:
        logger.warning("Dropped %d rows with missing OHLCV values from %s", n_dropped, path)

    df = df.sort_values("Date").set_index("Date")
    df.index.name = "Date"
    return df[["Open", "High", "Low", "Close", "Volume"]]


# Download daily OHLCV data from Yahoo Finance
def download_ohlcv_yf(
    tickers: Iterable[str],
    start: str,
    end: str,
    out_dir: str | Path,
    auto_adjust: bool = True,
) -> dict[str, str]:
    try:
        import yfinance as yf
    except ImportError as e:
        raise ImportError(
            "yfinance is required for live downloads: pip install yfinance"
        ) from e

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    status: dict[str, str] = {}

    for ticker in tickers:
        yf_symbol = f"{ticker}.NS"
        try:
            df = yf.download(
                yf_symbol, start=start, end=end, auto_adjust=auto_adjust, progress=False
            )
            if df.empty:
                status[ticker] = "no data returned"
                logger.warning("No data for %s", yf_symbol)
                continue

            df = df.reset_index()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            df = df.rename(columns={"Date": "Date"})[
                ["Date", "Open", "High", "Low", "Close", "Volume"]
            ]
            df.to_csv(out_dir / f"{ticker}.csv", index=False)
            status[ticker] = "ok"
            logger.info("Downloaded %s: %d rows", ticker, len(df))
        except Exception as e:
            status[ticker] = f"error: {e}"
            logger.error("Failed to download %s: %s", ticker, e)

    return status
