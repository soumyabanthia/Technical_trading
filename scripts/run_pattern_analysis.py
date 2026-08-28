import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data.loader import load_ohlcv_csv
from src.indicators.indicators import add_all_indicators
from src.patterns.candlestick import detect_all_patterns
from src.statistics.forward_returns import (
    compute_forward_returns,
    pattern_forward_return_summary,
    flag_low_sample_size,
)
from src.statistics.volume_confirmation import add_volume_confirmation
from src.trend.dow_theory import find_swing_points, classify_trend_from_swings

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
TABLES_DIR = ROOT / "reports" / "tables"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


# Process indicators and pattern analysis for a single ticker
def process_ticker(csv_path: Path) -> dict:
    ticker = csv_path.stem
    df = load_ohlcv_csv(csv_path)
    df = add_all_indicators(df)
    df["swing_high"] = find_swing_points(df)["swing_high"]
    df["swing_low"] = find_swing_points(df)["swing_low"]
    df["trend"] = classify_trend_from_swings(df)

    patterns_long = detect_all_patterns(df)
    patterns_long["ticker"] = ticker
    patterns_long = add_volume_confirmation(patterns_long, df)

    fwd_returns = compute_forward_returns(df["Close"])
    summary = pattern_forward_return_summary(patterns_long, fwd_returns)
    summary = flag_low_sample_size(summary)
    summary["ticker"] = ticker

    df.to_csv(PROCESSED_DIR / f"{ticker}_with_indicators.csv")
    patterns_long.to_csv(PROCESSED_DIR / f"{ticker}_patterns.csv", index=False)

    n_patterns = len(patterns_long)
    n_vol_confirmed = int(patterns_long["volume_confirmed"].sum())
    print(f"[{ticker}] {len(df)} bars | {n_patterns} pattern occurrences "
          f"({n_vol_confirmed} volume-confirmed)")

    return {"df": df, "patterns_long": patterns_long, "summary": summary}


# Run pattern analysis across all CSV files in data/raw
def main():
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {RAW_DIR}. Run scripts/download_data.py first "
              f"(requires internet access) or add TATACONSUM_2024.csv.")
        sys.exit(1)

    all_summaries = []
    for csv_path in csv_files:
        result = process_ticker(csv_path)
        all_summaries.append(result["summary"])

    combined = pd.concat(all_summaries, ignore_index=True)
    combined.to_csv(TABLES_DIR / "pattern_forward_return_summary.csv", index=False)
    print(f"\nWrote combined pattern summary to {TABLES_DIR / 'pattern_forward_return_summary.csv'}")

    low_conf_pct = combined["low_confidence"].mean() * 100
    print(f"NOTE: {low_conf_pct:.0f}% of pattern/horizon rows are flagged low_confidence "
          f"(n < {20}). With {len(csv_files)} ticker(s) of data currently available, "
          f"treat forward-return numbers as exploratory, not tradable evidence.")


if __name__ == "__main__":
    main()
