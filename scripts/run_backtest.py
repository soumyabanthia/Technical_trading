import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data.loader import load_ohlcv_csv
from src.indicators.indicators import add_all_indicators
from src.backtest.signals import generate_baseline_signals, generate_relaxed_signals
from src.backtest.engine import run_backtest, buy_and_hold_equity_curve
from src.backtest.metrics import full_report
from src.visualization.charts import (
    plot_price_with_patterns,
    plot_price_with_trend,
    plot_indicator_panel,
    plot_equity_curves,
    plot_drawdown,
)
from src.patterns.candlestick import detect_all_patterns
from src.trend.dow_theory import find_swing_points, classify_trend_from_swings

RAW_DIR = ROOT / "data" / "raw"
FIG_DIR = ROOT / "reports" / "figures"
TABLES_DIR = ROOT / "reports" / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

INITIAL_CAPITAL = 1_000_000.0


# Run backtest strategies and generate charts for a ticker
def run_for_ticker(csv_path: Path) -> dict:
    ticker = csv_path.stem
    df = load_ohlcv_csv(csv_path)
    df = add_all_indicators(df)

    df_baseline = generate_baseline_signals(df.copy())
    df_relaxed = generate_relaxed_signals(df.copy())

    bh_curve = buy_and_hold_equity_curve(df, initial_capital=INITIAL_CAPITAL)
    strat_result = run_backtest(df_baseline, initial_capital=INITIAL_CAPITAL)
    relaxed_result = run_backtest(df_relaxed, initial_capital=INITIAL_CAPITAL)

    bh_report = full_report(bh_curve, pd.DataFrame(columns=["return_pct", "holding_days"]))
    strat_report = full_report(strat_result.equity_curve, strat_result.trades_df)
    relaxed_report = full_report(relaxed_result.equity_curve, relaxed_result.trades_df)

    patterns_long = detect_all_patterns(df)
    plot_price_with_patterns(df, patterns_long, FIG_DIR / f"{ticker}_price_patterns.png", title=f"{ticker}: Price with Detected Candlestick Patterns")

    swings = find_swing_points(df)
    trend = classify_trend_from_swings(df)
    plot_price_with_trend(df, swings, trend, FIG_DIR / f"{ticker}_price_trend.png", title=f"{ticker}: Price with Swing Structure & Trend Classification")

    plot_indicator_panel(df, FIG_DIR / f"{ticker}_rsi_macd.png", title=f"{ticker}: RSI(14) and MACD(12,26,9)")

    plot_equity_curves(
        {
            "Buy & Hold": bh_curve,
            "Strategy 1 (baseline, strict)": strat_result.equity_curve,
            "Strategy 1b (relaxed, robustness check)": relaxed_result.equity_curve,
        },
        FIG_DIR / f"{ticker}_equity_curves.png",
        title=f"{ticker}: Equity Curve — Buy & Hold vs Strategy Variants",
    )
    plot_drawdown(relaxed_result.equity_curve, FIG_DIR / f"{ticker}_drawdown.png", title=f"{ticker}: Strategy 1b Drawdown")

    strat_result.trades_df.to_csv(TABLES_DIR / f"{ticker}_trades_baseline.csv", index=False)
    relaxed_result.trades_df.to_csv(TABLES_DIR / f"{ticker}_trades_relaxed.csv", index=False)

    return {
        "ticker": ticker,
        "buy_and_hold": bh_report,
        "strategy_1_baseline": strat_report,
        "strategy_1b_relaxed": relaxed_report,
        "n_bars": len(df),
    }


# Run backtest across all tickers and save results
def main():
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {RAW_DIR}.")
        sys.exit(1)

    all_results = {}
    for csv_path in csv_files:
        print(f"Running backtest for {csv_path.stem} ...")
        res = run_for_ticker(csv_path)
        all_results[res["ticker"]] = res
        print(f"  Buy&Hold   total_return={res['buy_and_hold']['total_return']:.4f}  "
              f"sharpe={res['buy_and_hold']['sharpe_ratio']:.3f}  "
              f"max_dd={res['buy_and_hold']['max_drawdown']:.4f}")
        print(f"  Strategy1  total_return={res['strategy_1_baseline']['total_return']:.4f}  "
              f"sharpe={res['strategy_1_baseline']['sharpe_ratio']:.3f}  "
              f"max_dd={res['strategy_1_baseline']['max_drawdown']:.4f}  "
              f"n_trades={res['strategy_1_baseline'].get('n_trades', 0)}")
        print(f"  Strategy1b total_return={res['strategy_1b_relaxed']['total_return']:.4f}  "
              f"sharpe={res['strategy_1b_relaxed']['sharpe_ratio']:.3f}  "
              f"max_dd={res['strategy_1b_relaxed']['max_drawdown']:.4f}  "
              f"n_trades={res['strategy_1b_relaxed'].get('n_trades', 0)}")

    with open(TABLES_DIR / "backtest_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nWrote {TABLES_DIR / 'backtest_results.json'}")
    print(f"Charts written to {FIG_DIR}")


if __name__ == "__main__":
    main()
