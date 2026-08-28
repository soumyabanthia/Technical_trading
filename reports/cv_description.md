# CV positioning

All wording below is constrained to what this project's code actually
produced (see `reports/final_report.md`). No Sharpe ratio, return figure, or
sample size is stated unless it matches a generated result exactly.

## A. One-line CV bullet

Built a reproducible Python backtesting framework (pandas, custom event-driven engine) implementing programmatic candlestick pattern detection, RSI/MACD/SMA signal generation, and no-look-ahead trade execution on NSE equity data, validated with a 29-test pytest suite.

## B. 2-line version

Rebuilt a manual technical-analysis exercise into a tested, reproducible Python research pipeline: programmatic detection of 8 candlestick patterns, Wilder RSI/MACD/SMA indicators computed from formula, and an event-driven backtester enforcing next-bar-open execution to eliminate look-ahead bias.
Investigated and explained a zero-trade backtest result by diagnosing a regime-dependent conflict between the strategy's mean-reversion (RSI) and trend-following (SMA) filters, rather than treating it as a failure — full methodology and honest sample-size caveats documented in a written research report.

## C. 3-line detailed version

Converted a university technical-analysis assignment (manual candlestick charting, Dow Theory trend calls, hand-logged trades) into a fully coded, tested research project: implemented SMA/RSI/MACD/ATR indicators from their published formulas, 8 rule-based candlestick pattern detectors, and a swing-high/swing-low trend-classification proxy — all covered by a 29-test pytest suite (indicator correctness, pattern logic, no-look-ahead execution, cash constraints, drawdown/Sharpe/profit-factor calculations).
Built a single-asset, event-driven backtest engine enforcing bar-close-signal → next-bar-open-execution to remove look-ahead bias, with transaction costs, slippage, and a trailing stop, and computed a full performance-metrics suite (Sharpe, Sortino, Calmar, max drawdown, profit factor, expectancy) directly from simulated trades rather than asserted claims.
Ran the pipeline on real NSE OHLCV data (TATACONSUM, CY2024): identified and diagnosed a genuine zero-trade result caused by conflicting mean-reversion/trend-following filter conditions, flagged all candlestick forward-return statistics below n=20 as low-confidence rather than overstating significance, and documented a defensible plan (working download script included) to extend the analysis to a 14-stock, 5-year Nifty FMCG universe.

## Notes on positioning honestly

- Do **not** claim "outperformed buy-and-hold" — on the current data, the
  strategy generated zero trades and buy-and-hold lost money; the honest
  story is the rigor of the pipeline and the diagnostic finding, not a
  trading win.
- If asked in an interview "what would you find with more data," a
  defensible answer is: "the architecture is built for it — I ran out of
  network access to pull it in the environment I built this in, not out of
  design effort," pointing to `scripts/download_data.py`.
- If you personally run `scripts/download_data.py` and get real multi-stock
  results, update this file and the README with the new numbers — do not
  reuse this file's current (zero-trade) framing once you have a bigger
  sample.
