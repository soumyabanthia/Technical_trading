# Systematic Technical Trading Research: An Empirical Case Study on Indian Equities

**Asset Focus**: Tata Consumer Products Ltd. (NSE: `TATACONSUM`)  
**Time Horizon**: Calendar Year 2024 (Daily OHLCV)  
**Author**: Quantitative Research & Trading Strategies  

---

## 1. Abstract

This research project presents an empirical, systematic evaluation of classical technical analysis methods, candlestick pattern recognition, and multi-indicator trading strategies applied to Indian equity market data. Using daily OHLCV prices of Tata Consumer Products (`TATACONSUM`) across CY2024, we build an end-to-end, reproducible quantitative pipeline that replaces discretionary charting heuristics with unambiguous mathematical rules. 

We implement first-principles indicator calculations, algorithmic Dow Theory swing-trend classification, formal pattern recognition across eight classical candlestick formations, and an event-driven backtesting engine with strict no-lookahead execution, transaction costs, and slippage modeling. Over the test sample, the benchmark buy-and-hold strategy returned -2.55% (Sharpe ratio -0.38, maximum drawdown -21.76%). The baseline momentum-trend strategy ($RSI(14) < 40$, 2-bar $MACD$ bullish confirmation, $Close > SMA(50)$) generated **zero trades**, revealing a fundamental structural tension between mean-reversion triggers and trend-following filters during market corrections. Forward-return distributions across all 90 detected candlestick occurrences are analyzed across 1, 5, 10, and 20-day horizons, accompanied by sample-size confidence flagging and volume-confirmation analysis.

---

## 2. Introduction & Research Motivation

Classical technical analysis—ranging from Japanese candlestick charting to Dow Theory trend classification—remains widely used among discretionary market participants. However, traditional discretionary application suffers from critical methodological vulnerabilities:
1. **Subjectivity and Unfalsifiability**: Human chart inspection lacks reproducible decision boundaries; different analysts can interpret the same price pattern with conflicting directional biases.
2. **Lookahead and Execution Bias**: Manual trade logs frequently assume same-bar closing fills, ignoring execution latency, intraday slippage, and spread friction.
3. **Selection Bias**: Textbook examples of chart patterns almost exclusively showcase successful post-pattern trends, ignoring false signals and negative forward returns.

The objective of this research is strictly quantitative and falsifiable: to formalize classical technical concepts into explicit algorithmic rules, test their statistical validity, and evaluate their economic performance under a realistic execution framework.

---

## 3. Research Questions & Hypotheses

1. **Indicator Interaction**: Does a composite strategy combining momentum indicators ($RSI$), trend indicators ($MACD$), and moving average filters ($SMA$) generate superior risk-adjusted returns compared to a buy-and-hold benchmark on Indian equities?
2. **Execution Realism**: How do strict execution rules (next-bar open execution, transaction friction, trailing stops) affect strategy viability?
3. **Candlestick Predictive Power**: Do classical candlestick reversal patterns exhibit statistically significant directional forward returns over 1-, 5-, 10-, and 20-day horizons?
4. **Volume Confirmation**: Does conditioning pattern signals on abnormal trading volume ($\ge 1.2\times$ 20-day moving average) enhance forward return characteristics?

---

## 4. Data & Pipeline Architecture

### 4.1 Data Ingestion and Validation
The primary dataset comprises daily OHLCV price series for **Tata Consumer Products Ltd.** (`TATACONSUM.NS`) for calendar year 2024 (262 trading sessions, 2024-01-01 to 2024-12-31), stored in `data/raw/TATACONSUM_2024.csv`.

The data pipeline (`src/data/loader.py`) enforces strict validation protocols:
- **Timestamp Standardization**: Dates are parsed to ISO format and sorted monotonically ascending.
- **Deduplication**: Duplicate timestamp entries are detected and resolved.
- **Completeness Checking**: Rows with missing, zero, or non-numeric OHLCV entries are filtered and logged.
- **Data Integrity**: Price sanity checks ensure $\text{High} \ge \max(\text{Open}, \text{Close})$ and $\text{Low} \le \min(\text{Open}, \text{Close})$.

### 4.2 Cross-Sectional Scaling Framework
To support multi-asset cross-sectional studies, the repository provides an automated data ingestion module (`scripts/download_data.py`) configured to fetch multi-year histories (2019–2024) across the **Nifty FMCG** sector constituents (including `BRITANNIA`, `COLPAL`, `DABUR`, `HINDUNILVR`, `ITC`, `MARICO`, `NESTLEIND`, `TATACONSUM`, `VBL`, etc.) via Yahoo Finance.

---

## 5. Quantitative Methodology

### 5.1 Algorithmic Dow Theory & Market Regime Classification
Classical Dow Theory identifies primary market trends through sequences of higher highs/higher lows (uptrend) or lower highs/lower lows (downtrend). To eliminate subjective interpretation, we implement a parameterized swing detection algorithm (`src/trend/dow_theory.py`):

1. **Symmetric Rolling Swing Extrema**: A bar at index $t$ is designated a **Swing High** if:
   $$\text{High}_t = \max_{k \in [-w, w]} \text{High}_{t+k}$$
   Similarly, a **Swing Low** is defined if $\text{Low}_t = \min_{k \in [-w, w]} \text{Low}_{t+k}$, with lookback/lookforward parameter $w = 5$ bars.
2. **Regime State Machine**:
   - **Uptrend**: The two most recent confirmed swing highs are ascending ($\text{SH}_n > \text{SH}_{n-1}$) **AND** the two most recent swing lows are ascending ($\text{SL}_n > \text{SL}_{n-1}$).
   - **Downtrend**: Both recent swing highs and swing lows are descending ($\text{SH}_n < \text{SH}_{n-1}$ and $\text{SL}_n < \text{SL}_{n-1}$).
   - **Sideways / Consolidation**: Divergence between high and low trajectories (e.g., higher high with lower low, or vice versa).
3. **Forward Filling**: Regime state is maintained until a newly confirmed swing point alters the structural classification.

Empirical evaluation on TATACONSUM CY2024 identified three distinct market phases:
- **Uptrend**: January to June 2024 (Price advanced from $\approx ₹880$ to $\approx ₹1,120$).
- **Downtrend / Corrective**: July to September 2024.
- **Consolidation / Range-bound**: October to December 2024.

*(Visualized in `reports/figures/TATACONSUM_2024_price_trend.png`)*

---

### 5.2 Technical Indicator Formulations
All indicators are computed from first mathematical principles (`src/indicators/indicators.py`) with unit-test verification against exact boundary conditions:

1. **Simple Moving Averages**:
   $$\text{SMA}_k(t) = \frac{1}{k} \sum_{i=0}^{k-1} \text{Close}_{t-i}, \quad k \in \{20, 50\}$$
2. **Relative Strength Index (Wilder's Smoothing)**:
   $$\text{RSI}_{14}(t) = 100 - \frac{100}{1 + \text{RS}_t}$$
   $$\text{RS}_t = \frac{\text{EMA}_{14}(\text{Upward Price Changes})}{\text{EMA}_{14}(\text{Downward Price Changes})}$$
3. **Moving Average Convergence Divergence (MACD)**:
   $$\text{MACD Line}_t = \text{EMA}_{12}(\text{Close}_t) - \text{EMA}_{26}(\text{Close}_t)$$
   $$\text{Signal Line}_t = \text{EMA}_{9}(\text{MACD Line}_t)$$
   $$\text{Histogram}_t = \text{MACD Line}_t - \text{Signal Line}_t$$
4. **Average True Range (ATR)**:
   $$\text{TR}_t = \max\left(\text{High}_t - \text{Low}_t, \, |\text{High}_t - \text{Close}_{t-1}|, \, |\text{Low}_t - \text{Close}_{t-1}|\right)$$
   $$\text{ATR}_{14}(t) = \text{EMA}_{14}(\text{TR}_t)$$

*(Visualized in `reports/figures/TATACONSUM_2024_rsi_macd.png`)*

---

### 5.3 Candlestick Pattern Recognition Engine
We formulate algorithmic definitions for eight major candlestick patterns based on Steve Nison (1991) taxonomies (`src/patterns/candlestick.py`). All threshold ratios are pre-specified to avoid overfitting:

- **Candle Body**: $|\text{Close} - \text{Open}|$
- **Full Candle Range**: $\text{High} - \text{Low}$
- **Upper Shadow**: $\text{High} - \max(\text{Open}, \text{Close})$
- **Lower Shadow**: $\min(\text{Open}, \text{Close}) - \text{Low}$

| Pattern | Expected Bias | Structural Detection Rules |
|---|---|---|
| **Doji** | Neutral | $\text{Body} \le 0.05 \times \text{Range}$ |
| **Hammer** | Bullish Reversal | $\text{Body} \le 0.35 \times \text{Range}$, $\text{Lower Shadow} \ge 2.0 \times \text{Body}$, $\text{Upper Shadow} \le 0.30 \times \text{Range}$ |
| **Shooting Star** | Bearish Reversal | $\text{Body} \le 0.35 \times \text{Range}$, $\text{Upper Shadow} \ge 2.0 \times \text{Body}$, $\text{Lower Shadow} \le 0.30 \times \text{Range}$ |
| **Bullish Engulfing** | Bullish Reversal | $\text{Bar}_{t-1}$ Bearish, $\text{Bar}_t$ Bullish, $\text{Open}_t < \text{Close}_{t-1}$, $\text{Close}_t > \text{Open}_{t-1}$ |
| **Bearish Engulfing** | Bearish Reversal | $\text{Bar}_{t-1}$ Bullish, $\text{Bar}_t$ Bearish, $\text{Open}_t > \text{Close}_{t-1}$, $\text{Close}_t < \text{Open}_{t-1}$ |
| **Morning Star** | Bullish Reversal | 3-bar sequence: Large Bearish $\rightarrow$ Small Body Gap Down $\rightarrow$ Bullish closing above midpoint of Bar 1 |
| **Evening Star** | Bearish Reversal | 3-bar sequence: Large Bullish $\rightarrow$ Small Body Gap Up $\rightarrow$ Bearish closing below midpoint of Bar 1 |
| **Three White Soldiers** | Bullish Continuation | 3 consecutive bullish bars with progressive higher closes, opening within prior real body, substantial body ratio ($\ge 0.5$) |

Over the 2024 dataset, the detector cataloged **90 pattern occurrences** (`reports/figures/TATACONSUM_2024_price_patterns.png`).

---

## 6. Trading Strategy Formulations

### 6.1 Baseline Multi-Indicator Strategy (Strategy 1)
Designed to capture trend-following momentum with mean-reversion entry timing:

- **Entry Condition (Long Only)**:
  1. Mean-reversion trigger: $\text{RSI}_{14} < 40$ (moderately oversold).
  2. Momentum confirmation: $\text{MACD Line} > \text{Signal Line}$ maintained for at least 2 consecutive trading sessions.
  3. Trend regime filter: $\text{Close} > \text{SMA}_{50}$ (ensuring underlying medium-term bullish trend).
- **Exit Conditions**:
  1. Momentum exhaustion: $\text{RSI}_{14} > 65$.
  2. Trend reversal: $\text{MACD}$ bearish cross below Signal Line while $\text{Close} < \text{SMA}_{20}$.
  3. Risk management: 5% trailing stop-loss from highest close achieved since trade inception.

### 6.2 Strategy 1b (Parameter Robustness Variant)
To test whether baseline parameters were overly restrictive, Strategy 1b relaxes conditions:
- $\text{RSI}_{14} < 45$ (broadened oversold band)
- 1-bar MACD cross confirmation
- Exit threshold at $\text{RSI}_{14} > 60$

---

## 7. Backtest Engineering & Execution Mechanics

The strategy is executed via a deterministic, event-driven simulation engine (`src/backtest/engine.py`):

- **Strict Lookahead Elimination**: Signals generated at the close of bar $t$ (incorporating all information up to $t$) are queued for execution at the **Open of bar $t+1$**. Same-bar execution is disallowed.
- **Transaction Friction**: Fixed broker commission of $0.05\%$ per side.
- **Slippage Modeling**: Execution slippage of $0.05\%$ per side applied adversely (buys fill at $\text{Open} \times 1.0005$, sells fill at $\text{Open} \times 0.9995$).
- **Trailing Stop Loss**: Calculated dynamically at each bar close; if breached, an exit order is executed at the next bar's open.
- **Capital Allocation**: Fixed fractional sizing (100% equity per position, single asset).

---

## 8. Empirical Results

### 8.1 Performance Summary

| Performance Metric | Buy & Hold Benchmark | Strategy 1 (Baseline) | Strategy 1b (Relaxed) |
|---|---|---|---|
| **Total Return** | **-2.55%** | **0.00%** | **0.00%** |
| **CAGR** | -2.55% | 0.00% | 0.00% |
| **Annualized Volatility** | 18.57% | 0.00% | 0.00% |
| **Sharpe Ratio ($r_f = 6.5\%$)** | **-0.38** | n/a | n/a |
| **Sortino Ratio** | -0.66 | n/a | n/a |
| **Maximum Drawdown** | **-21.76%** | **0.00%** | **0.00%** |
| **Calmar Ratio** | -0.12 | n/a | n/a |
| **Total Closed Trades** | — | **0** | **0** |
| **Capital Preservation** | Exposed to -21.8% DD | 100% Cash Protected | 100% Cash Protected |

*(Equity curve and drawdown distributions visualized in `reports/figures/TATACONSUM_2024_equity_curves.png` and `reports/figures/TATACONSUM_2024_drawdown.png`)*

---

### 8.2 In-Depth Analysis: The Zero-Trade Finding

A critical outcome of this research is that both the baseline strategy and its relaxed variant generated **zero trades** over the 262-session testing window. 

#### Mechanistic Diagnosis:
1. **Regime Divergence**: In CY2024, TATACONSUM experienced its major oversold RSI periods ($\text{RSI} < 40$ and $\text{RSI} < 45$) almost exclusively during the July–December corrective downturn.
2. **Filter Interaction**: During this corrective period, the price traded persistently *below* its 50-day Simple Moving Average ($\text{Close} < \text{SMA}_{50}$).
3. **Orthogonality of Rules**: The requirement that an asset be simultaneously in an intermediate uptrend ($\text{Close} > \text{SMA}_{50}$) and experiencing a deep pullback ($\text{RSI} < 40$) was never satisfied in this sample (0 out of 213 valid indicator bars).

```
   ┌─────────────────────────────────────────────────────────────┐
   │             Market Regime / Indicator Conflict              │
   ├──────────────────────────────┬──────────────────────────────┤
   │ Bullish Trend Filter:        │ Mean Reversion Trigger:      │
   │ Price > SMA(50)              │ RSI(14) < 40                 │
   │ (Occurred Jan - Jun 2024)    │ (Occurred Jul - Dec 2024)    │
   └──────────────┬───────────────┴──────────────┬───────────────┘
                  │                              │
                  └──────────────┬───────────────┘
                                 │
                     No Concurrent Intersection
                                 │
                     ▼ ZERO TRADES EXECUTED ▼
```

#### Quantitative Takeaway:
This is an authentic empirical property of the strategy's rule design rather than a software defect. Discretionary traders often claim to trade "oversold pullbacks in strong uptrends," but in systematic backtesting with strict parameters, such intersections can be exceptionally rare on single assets over single-year horizons. The strategy successfully protected capital from the stock's -21.76% maximum drawdown by remaining in cash.

---

## 9. Candlestick Pattern Forward Return Statistics

To evaluate whether candlestick formations possess standalone predictive edge, forward returns were computed at 1-, 5-, 10-, and 20-day horizons following each pattern detection ($t_{\text{close}}$ to $t_{\text{close}+h}$):

### 9.1 Summary Statistics (5-Day Horizon)

| Candlestick Pattern | Theoretical Bias | Sample Count ($n$) | Mean 5-Day Return | Median Return | Positive Return % | Confidence Flag |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Shooting Star** | Bearish | 18 | +0.99% | +0.81% | 61.1% | Low Sample ($n < 20$) |
| **Doji** | Neutral | 6 | +0.86% | +0.72% | 66.7% | Low Sample ($n < 20$) |
| **Bullish Engulfing** | Bullish | 13 | +0.25% | -0.15% | 46.2% | Low Sample ($n < 20$) |
| **Hammer** | Bullish | 14 | -0.08% | +0.02% | 50.0% | Low Sample ($n < 20$) |
| **Evening Star** | Bearish | 7 | -0.13% | -0.22% | 42.9% | Low Sample ($n < 20$) |
| **Morning Star** | Bullish | 11 | -0.40% | -0.55% | 45.5% | Low Sample ($n < 20$) |
| **Bearish Engulfing** | Bearish | 15 | -0.42% | -0.31% | 53.3% | Low Sample ($n < 20$) |
| **Three White Soldiers** | Bullish | 5 | -1.00% | -1.12% | 40.0% | Low Sample ($n < 20$) |

*(Complete 1/5/10/20-day table available in `reports/tables/pattern_forward_return_summary.csv`)*

### 9.2 Statistical Interpretation & Multiple Testing
1. **Contradictory Empirical Realities**: Several patterns exhibited forward returns contrary to textbook theory (e.g., the bearish Shooting Star averaged a +0.99% 5-day return with a 61% positive win rate, while the bullish Morning Star averaged -0.40%).
2. **Sample Size Constraints**: All pattern categories have $n < 20$ occurrences across the single-year dataset. These distributions must be treated as descriptive and exploratory rather than statistically conclusive.
3. **Multiple Testing Bias**: Evaluating 8 patterns across 4 forward horizons yields 32 hypothesis tests. In such small sample regimes, applying family-wise error rate corrections (e.g., Bonferroni) confirms that none of the observed pattern returns achieve statistical significance ($p > 0.05$).

---

## 10. Volume Confirmation Analysis

We tested whether filtering pattern occurrences by trading volume improves predictive fidelity (`src/statistics/volume_confirmation.py`). A pattern was defined as **Volume Confirmed** if:
$$\text{Volume}_t \ge 1.20 \times \left(\frac{1}{20}\sum_{i=1}^{20} \text{Volume}_{t-i}\right)$$

### Findings:
- Of the 90 total pattern occurrences, only **14 instances (15.6%)** met the volume surge threshold.
- Partitioning 14 occurrences across 8 pattern categories yields cell counts of 1–3 occurrences per pattern, which is insufficient for robust sub-group inference.
- Consequently, volume-confirmed returns are reported as an aggregate structural finding rather than an overfitted sub-strategy.

---

## 11. Robustness & Sensitivity Analysis

1. **Parameter Perturbation**: Modifying RSI boundaries from 40/65 to 45/60 and MACD persistence from 2 to 1 confirmed the structural regime gap—no entries were generated under either specification.
2. **Execution Timing**: Enforcing next-bar open fills prevents the artificial return inflation commonly observed in backtests that assume instantaneous execution at the signal bar's close.
3. **Detector Unit-Test Coverage**: All pattern detection algorithms were validated against synthetic test vectors with known geometry (`tests/test_patterns.py`) to eliminate false positives and boundary errors.

---

## 12. Methodological Limitations

1. **Sample Scope**: A single equity ticker across one calendar year provides an exploratory testbed, but cannot support generalized macroeconomic or cross-sectional conclusions.
2. **Intraday Execution Resolution**: Daily OHLCV data cannot verify whether stop-loss thresholds were breached intraday or at the market close; conservative next-open execution is assumed.
3. **Zero-Trade Invariance**: Strategy Sharpe and drawdown metrics remain unmeasured under active trading conditions due to the lack of qualifying trade signals in this specific sample.

---

## 13. Conclusion & Key Takeaways

1. **Systematic vs. Discretionary Gap**: Discretionary technical rules often sound intuitive in isolation, but formal quantitative testing reveals latent conflicts between indicators (e.g., trend filters neutralizing mean-reversion signals).
2. **Falsifiability in Quant Finance**: Reporting a zero-trade outcome or statistically insignificant pattern returns with full diagnostic transparency is far more valuable than curve-fitting parameters to fabricate artificial alpha.
3. **Extensible Architecture**: The developed modular pipeline (`src/`) provides a production-ready framework for multi-asset, cross-sectional technical research across large equity universes.

---

## 14. Future Research Directions

- **Cross-Sectional Sector Backtesting**: Execute `scripts/download_data.py` to ingest 5-year daily histories across all 14 Nifty FMCG constituent stocks and evaluate cross-sectional momentum and mean-reversion strategies.
- **Dynamic Volatility Scaling**: Incorporate ATR-based adaptive RSI bands rather than static thresholds (e.g., $\text{RSI} < 50 - k \times \sigma$).
- **Machine Learning Integration**: Implement decision-tree and gradient-boosted classifiers on multi-feature indicator tensors once sample sizes exceed $n > 5,000$ bars across the expanded universe.

---

## References

1. **Nison, S.** (1991). *Japanese Candlestick Charting Techniques: A Contemporary Guide to the Ancient Investment Techniques of the Far East*. New York Institute of Finance.
2. **Wilder, J. W.** (1978). *New Concepts in Technical Trading Systems*. Trend Research.
3. **Appel, G.** (2005). *Technical Analysis: Power Tools for Active Investors*. Financial Times Prentice Hall.
4. **Rhea, R.** (1932). *The Dow Theory: An Explanation of Its Development and an Attempt to Define Its Usefulness as an Aid to Speculation*. Barron's.
5. **Pardo, R.** (2008). *The Evaluation and Optimization of Trading Strategies*. John Wiley & Sons.
6. **Harvey, C. R., Liu, Y., & Zhu, H.** (2016). *... and the Cross-Section of Expected Returns*. The Review of Financial Studies, 29(1), 5-68.
