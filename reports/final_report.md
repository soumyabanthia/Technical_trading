# Systematic Technical Trading Research: TATACONSUM Case Study

## 1. Abstract

This report converts a manual technical-analysis assignment on Tata Consumer
Products (TATACONSUM) into a reproducible, code-based research pipeline. We
replace hand-identified candlestick patterns and Dow Theory trend calls with
programmatic detection, and replace a manually-logged 4-trade backtest with
an event-driven, no-look-ahead backtesting engine. On the CY2024 TATACONSUM
sample, buy-and-hold returned -2.55% (Sharpe -0.38, max drawdown -21.8%),
and the baseline RSI/MACD/SMA strategy generated **zero trades**, because
its oversold (RSI) and uptrend (price>SMA50) conditions never coincided in
this sample — a genuine, investigated finding rather than an artefact.
Candlestick pattern forward-return statistics were computed for all 90
detected occurrences but every pattern/horizon combination has fewer than 20
occurrences and is explicitly flagged low-confidence.

## 2. Introduction

Manual technical analysis — reading candlestick charts and applying Dow
Theory by eye — is inherently subjective and unfalsifiable: two analysts can
label the same chart differently, and "it worked once" is not evidence of an
edge. This project's goal is methodological, not promotional: to show what
happens when the same ideas (candlestick patterns, trend structure, an
RSI/MACD/SMA strategy) are made fully explicit, testable, and run through a
backtest that cannot look ahead.

## 3. Research question

Do classical candlestick patterns and a rule-based RSI/MACD/SMA strategy
produce a statistically and economically meaningful edge over buy-and-hold
on an NSE FMCG stock, once look-ahead bias, transaction costs, and sample
size are handled rigorously?

## 4. Data

**Source**: `data/raw/TATACONSUM_2024.csv`, extracted directly from the
original assignment's Excel workbook (`Price Data` sheet), covering
2024-01-01 to 2024-12-31, 262 rows, daily OHLCV.

**Data-quality handling** (`src/data/loader.py`): dates parsed and sorted
ascending; duplicate dates de-duplicated (last kept, logged); rows with any
missing OHLCV value dropped (logged); all price/volume columns coerced to
numeric.

**Disclosed limitation**: this environment has no internet access to
independently verify these prices against NSE/Yahoo Finance (both are
blocked at the network level in the sandbox this project was built in — see
README). The figures should be treated as representative of the assignment's
original dataset, not independently re-verified against an exchange feed.

**Planned extension**: `scripts/download_data.py` downloads 2019–2024 daily
OHLCV for 14 Nifty FMCG constituents via `yfinance`, chosen over scraping
`nseindia.com` directly because NSE's site requires session/cookie handling
and aggressively rate-limits automated clients, whereas `yfinance` is the
most widely used, actively maintained free wrapper for NSE tickers
(`<SYMBOL>.NS`). This has not yet been executed against real data in this
environment (see README).

## 5. Methodology — Dow Theory / trend

Classical Dow Theory trend identification is discretionary; there is no
universally agreed mechanical definition of a "primary trend." We implement
a transparent proxy (`src/trend/dow_theory.py`), not a claim of having
automated Dow Theory:

1. Swing highs/lows via a symmetric rolling window (±5 bars): a bar is a
   swing high if its High is the maximum High in the 11-bar window centred
   on it (analogous for swing lows).
2. Trend state updates at each new confirmed swing: **uptrend** if the two
   most recent swing highs are rising AND the two most recent swing lows are
   rising; **downtrend** if both are falling; **sideways** otherwise. State
   is forward-filled between swing confirmations.

This produced three broad regimes across 2024: an uptrend Jan–Jun (price
~880 → ~1120), a downtrend Jul–Sep, and a choppy/sideways Oct–Dec — visible
in `reports/figures/TATACONSUM_2024_price_trend.png`.

## 6. Methodology — candlestick detection

Eight patterns implemented from Nison (1991) definitions, each as an
explicit boolean rule over body/shadow/range ratios (`src/patterns/candlestick.py`),
unit-tested individually (`tests/test_patterns.py`). No pattern was hand-fit
to this dataset — thresholds (e.g. "body ≤ 5% of range" for a Doji) were
fixed from standard definitions before running detection.

**Occurrences detected in 2024**: 90 total across 8 pattern types (see
`reports/figures/TATACONSUM_2024_price_patterns.png`), ranging from 5
(Three White Soldiers) to 18 (Shooting Star).

## 7. Methodology — technical indicators

SMA(20,50), RSI(14, Wilder smoothing), MACD(12,26,9), ATR(14) — implemented
directly from their standard formulas (`src/indicators/indicators.py`), not
via an opaque library call, so every calculation is auditable and unit-
tested against known boundary conditions (e.g., a strictly increasing price
series must yield RSI=100).

## 8. Baseline strategy (Strategy 1)

Rules (fully machine-readable, `src/backtest/signals.py`):

- **Buy** when RSI(14) < 40 AND MACD > MACD-signal has held for 2
  consecutive bars AND Close > SMA(50).
- **Sell** when RSI(14) > 65, OR MACD crosses below signal while Close <
  SMA(20).
- **Stop-loss**: 5% trailing stop from the highest close since entry.

This retains the original assignment's RSI/MACD/SMA concept but replaces
its "enter when the chart looks bullish" discretion with an unambiguous,
testable rule set.

## 9. Backtest engineering

Implemented as a single-asset, event-driven engine (`src/backtest/engine.py`):

- **No look-ahead, enforced structurally**: a signal computed from bar *t*'s
  close can only be executed at bar *t+1*'s open. This directly fixes the
  original assignment's implicit same-bar-close execution assumption — the
  single most common backtest correctness bug — and is unit-tested
  (`tests/test_backtest_engine.py::test_no_lookahead_flat_until_execution_bar`).
- **Transaction costs**: 0.05% of trade notional per side.
- **Slippage**: 0.05% per side, applied against the trader (buys fill
  higher, sells fill lower).
- **Stop-loss execution**: triggered at bar close, executed at the *next*
  bar's open (consistent with the no-look-ahead rule; we cannot verify
  intraday execution at an exact stop price from daily OHLC alone, so this
  is a conservative assumption, documented rather than silently assumed
  away).
- **Position sizing**: fixed-fractional — 100% of available cash per entry
  (single-asset case; generalises directly to equal-capital-allocation in
  the planned multi-stock extension).
- **Long only**, matching the original assignment's framing.

## 10. Results

| Metric | Buy & Hold | Strategy 1 (baseline) | Strategy 1b (relaxed, robustness check) |
|---|---|---|---|
| Total return | -2.55% | 0.00% | 0.00% |
| CAGR | -2.55% | 0.00% | 0.00% |
| Annualized volatility | 18.57% | 0.00% | 0.00% |
| Sharpe ratio (rf=6.5%) | -0.38 | n/a | n/a |
| Sortino ratio | -0.66 | n/a | n/a |
| Max drawdown | -21.76% | 0.00% | 0.00% |
| Calmar ratio | -0.12 | n/a | n/a |
| Number of trades | — | 0 | 0 |

**Strategy 1b** (a documented, pre-specified robustness check — relaxed RSI
thresholds to 45/60 and reduced the MACD confirmation window from 2 bars to
1) was run *once*, not swept over many parameter combinations, to test
whether the zero-trade result was an artefact of an overly strict rule
combination. It was not: even relaxed, the MACD-bullish-cross AND
RSI-oversold AND price-above-SMA50 conditions never coincided (0 of 213
valid bars satisfy the relaxed combination either).

### Why zero trades is a real finding, not a bug

Diagnostics (reproducible via `scripts/run_backtest.py` and shown in
`reports/figures/TATACONSUM_2024_price_trend.png`): TATACONSUM's oversold
RSI readings in 2024 clustered in the Jul–Dec corrective phase, when price
was trading *below* its 50-day SMA. The baseline rule's trend filter (Close
> SMA50) is specifically designed to avoid buying into downtrends — so it
correctly filtered out every oversold signal that occurred during the
period when the stock was, in fact, in a downtrend. This demonstrates a
known tension between mean-reversion signals (RSI) and trend-following
filters (SMA): they can be mutually exclusive depending on market regime.
The backtest engine itself is verified correct via unit tests using
synthetic price series specifically engineered to trigger entries, exits,
stop-losses, and cost deductions (`tests/test_backtest_engine.py`), so this
is a statement about the strategy's rule design on this specific sample —
not a claim that the code cannot execute a trade.

## 11. Candlestick forward-return statistics

For every detected pattern, forward returns were computed at 1/5/10/20-day
horizons from the close of the pattern bar (`src/statistics/forward_returns.py`),
with no look-ahead (patterns are detected using only information available
through the pattern bar's own close).

Selected results at the 5-day horizon (full table:
`reports/tables/pattern_forward_return_summary.csv`):

| Pattern | Direction | n | Mean 5-day fwd return | % positive |
|---|---|---|---|---|
| Shooting Star | bearish | 18 | +0.99% | 61% |
| Doji | neutral | 6 | +0.86% | 67% |
| Bullish Engulfing | bullish | 13 | +0.25% | 46% |
| Hammer | bullish | 14 | -0.08% | 50% |
| Evening Star | bearish | 7 | -0.13% | 43% |
| Morning Star | bullish | 11 | -0.40% | 45% |
| Bearish Engulfing | bearish | 15 | -0.42% | 53% |
| Three White Soldiers | bullish | 5 | -1.00% | 40% |

**Every row above is flagged `low_confidence` (n < 20)** in the underlying
data. Notably, several results run counter to textbook expectation (e.g.
Shooting Star, a bearish reversal signal, shows a positive mean forward
return here) — this is exactly what should be expected from small,
noisy samples and is reported as-is rather than explained away, per this
project's data-integrity rules (Section 27 of the original project brief:
never fabricate or selectively present results).

**Multiple-testing caveat**: 8 patterns × 4 horizons = 32 statistical
comparisons were run on one dataset. No correction for multiple comparisons
(e.g. Bonferroni) has been applied because, given the sample sizes involved,
none of these results would survive such a correction regardless — the
honest conclusion is that this sample cannot support pattern-level trading
conclusions, full stop.

## 12. Volume-confirmation enhancement (Strategy 2 concept)

Of the four candidate enhancements considered (volume confirmation, trend-
conditioned pattern reliability scoring, sector-relative analysis, ML
classification), **volume confirmation** was selected and its definition
fixed *before* running it: a pattern occurrence is volume-confirmed if that
bar's volume is ≥ 1.2× the prior 20-day average volume (computed excluding
the pattern bar itself, to avoid the pattern day's own volume inflating its
baseline).

**Result**: only 14 of 90 occurrences (15.6%) were volume-confirmed.
Breaking this down further by individual pattern would leave 1-3
occurrences per cell — not analytically meaningful — so this is reported at
the aggregate level only, rather than manufacturing a false level of
granularity.

ML-based signal classification was explicitly considered and rejected for
this sample size: fitting a classifier on ~250 rows with single-digit
counts per pattern class would be a textbook overfitting example, which
this project's own methodology rules (see README, Section 9 of the original
brief) are designed to avoid.

## 13. Out-of-sample validation

**Not performed in this iteration.** With only one calendar year of data, a
defensible train/validation/test split (e.g. train on 8 months, test on 4)
would leave too few observations in each split to draw any conclusion at
all — doing so would create a false appearance of rigor. This is listed
under Future Work rather than implemented with an inadequate sample.

## 14. Robustness checks performed

- **Strict vs. relaxed signal thresholds** (Section 10): result (zero
  trades) was unchanged, ruling out "one specific threshold happened to be
  unlucky" as the explanation.
- **Transaction cost sensitivity**: not applicable this iteration (zero
  trades in both variants means no costs were incurred to test sensitivity
  on).
- **Pattern detector unit tests**: every pattern function is tested against
  hand-constructed cases designed to be unambiguously true/false positives/
  negatives (`tests/test_patterns.py`).

## 15. Discussion

The central, defensible finding from this iteration is methodological
rather than a trading discovery: making the original assignment's strategy
fully explicit revealed that its two filtering conditions (RSI oversold,
price above SMA50) are regime-dependent and can be mutually exclusive — a
fact that manual, discretionary chart-reading is unlikely to surface with
this precision, because a human analyst applying "buy when oversold in an
uptrend" informally would likely relax one condition without noticing the
interaction. This is exactly the kind of insight systematic backtesting is
supposed to produce, even when (especially when) the headline result is "no
trades," rather than a manufactured positive outcome.

## 16. Limitations

1. Single stock, single year — every quantitative conclusion here is
   exploratory, explicitly not evidence of a tradable edge.
2. No independent verification of the underlying price data against a live
   exchange feed (no internet access in this environment).
3. Zero backtested trades means Strategy 1's risk/return properties (Sharpe,
   drawdown behaviour under live trading) remain untested on this sample.
4. No out-of-sample or walk-forward validation performed (see Section 13).
5. Transaction cost assumptions are a documented estimate, not sourced from
   a specific broker's fee schedule.

## 17. Conclusion

This project converts a manual, single-stock technical-analysis assignment
into a reproducible, tested, honestly-reported research pipeline. The
current, real result — zero baseline-strategy trades and a low-confidence
candlestick forward-return dataset — is not a "success" in the sense of
beating buy-and-hold, but it is a rigorous, defensible, and extensible
result, unlike the original assignment's four hand-picked trades. The
architecture is built to scale directly to a multi-stock, multi-year
universe via `scripts/download_data.py`.

## 18. Future research

- Execute the full Nifty FMCG universe download and re-run the entire
  pipeline unchanged (architecture already supports this).
- Walk-forward validation once sufficient history exists.
- Sector-relative or trend-conditioned pattern reliability scoring once
  cross-sectional data is available.
- Reconsider ML-based signal classification once sample size supports it.

## References

- Nison, S. (1991). *Japanese Candlestick Charting Techniques*. New York Institute of Finance.
- Wilder, J.W. (1978). *New Concepts in Technical Trading Systems*. Trend Research.
- Appel, G. (2005). *Technical Analysis: Power Tools for Active Investors*. FT Press.
- Rhea, R. (1932). *The Dow Theory*. Barron's.
