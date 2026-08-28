import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.loader import download_ohlcv_yf

TICKERS = [
    "BRITANNIA",
    "COLPAL",
    "DABUR",
    "EMAMILTD",
    "GILLETTE",
    "GODREJCP",
    "HINDUNILVR",
    "ITC",
    "MARICO",
    "NESTLEIND",
    "RADICO",
    "TATACONSUM",
    "UBL",
    "VBL",
]
START = "2019-01-01"
END = "2024-12-31"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


# Download data for all configured tickers
def main():
    print(f"Downloading {len(TICKERS)} tickers from {START} to {END} into {OUT_DIR} ...")
    status = download_ohlcv_yf(TICKERS, START, END, OUT_DIR)
    ok = [t for t, s in status.items() if s == "ok"]
    failed = {t: s for t, s in status.items() if s != "ok"}
    print(f"\nSucceeded: {len(ok)}/{len(TICKERS)}")
    if failed:
        print("Failed tickers (investigate before proceeding):")
        for t, s in failed.items():
            print(f"  {t}: {s}")
    print("\nDone. Next: python scripts/run_pattern_analysis.py")


if __name__ == "__main__":
    main()
