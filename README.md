# Technical Trading Research

A modular, reproducible quantitative trading research framework for algorithmic technical analysis, candlestick pattern recognition, and event-driven backtesting on Indian equity markets.

---

## Overview

This project provides an end-to-end Python pipeline designed to systematically evaluate classical technical analysis concepts with institutional-grade rigor. It replaces discretionary charting rules with unambiguous mathematical definitions, tests them against historical daily price series, and measures their economic performance using an event-driven backtesting engine with realistic frictions (next-bar execution, transaction costs, slippage, and trailing stop losses).

Key case study: **Tata Consumer Products Ltd. (NSE: `TATACONSUM`)** for calendar year 2024.

---

## Core Capabilities

- **Technical Indicators**: First-principles implementations of Simple Moving Averages (SMA), Exponential Moving Averages (EMA), Relative Strength Index (RSI with Wilder's smoothing), Moving Average Convergence Divergence (MACD), and Average True Range (ATR).
- **Algorithmic Dow Theory**: Rule-based swing-high / swing-low detection with rolling extrema windows ($w=\pm 5$) and state-machine trend classification (`uptrend`, `downtrend`, `sideways`).
- **Candlestick Pattern Recognition Engine**: Mathematical formalization of 8 classical candlestick patterns (Doji, Hammer, Shooting Star, Bullish Engulfing, Bearish Engulfing, Morning Star, Evening Star, Three White Soldiers) following Steve Nison's structural definitions.
- **Event-Driven Backtesting Engine**: Deterministic bar-by-bar execution eliminating lookahead bias (signals generated at bar $t$ close are executed at bar $t+1$ open), customizable commissions (0.05%), execution slippage (0.05%), and dynamic trailing stops (5%).
- **Performance Analytics & Reporting**: Comprehensive risk/return metrics (Sharpe ratio, Sortino ratio, CAGR, max drawdown, Calmar ratio, win rate, profit factor, trade expectancy) and forward-return statistical summaries across multi-period horizons (1, 5, 10, 20 days).
- **Volume Confirmation Filter**: Evaluates whether abnormal volume surges ($\ge 1.2\times$ 20-day moving average) enhance pattern predictive value.
- **Automated Visualization**: Publication-ready charts for price patterns, swing trends, indicator panels, portfolio equity curves, and underwater drawdowns.

---

## Project Structure

```
technical-trading-research/
├── config/
│   └── config.yaml                 # Strategy parameters, costs, risk-free rate, pattern settings
├── data/
│   ├── raw/                        # Raw historical OHLCV CSV data (e.g., TATACONSUM_2024.csv)
│   └── processed/                  # Feature-engineered datasets with indicators and pattern flags
├── reports/
│   ├── figures/                    # High-resolution generated charts (PNG)
│   ├── tables/                     # Backtest results JSON, trade logs, and pattern statistics
│   └── final_report.md             # Comprehensive research report and empirical analysis
├── scripts/
│   ├── download_data.py            # Multi-year data fetcher for Nifty FMCG universe via Yahoo Finance
│   ├── run_backtest.py             # Script to execute backtests and generate visual reports
│   └── run_pattern_analysis.py     # Script to compute indicator features and forward-return stats
├── src/
│   ├── backtest/
│   │   ├── engine.py               # Event-driven backtest simulation engine
│   │   ├── metrics.py              # Performance, risk, and trade statistics calculations
│   │   └── signals.py              # Strategy signal generation logic
│   ├── data/
│   │   └── loader.py               # Data ingestion, schema validation, and cleanup
│   ├── indicators/
│   │   └── indicators.py           # First-principles technical indicator formulas
│   ├── patterns/
│   │   └── candlestick.py          # Candlestick pattern detection rules
│   ├── statistics/
│   │   ├── forward_returns.py      # Multi-horizon forward return calculations and summaries
│   │   └── volume_confirmation.py  # Rolling volume surge confirmation logic
│   ├── trend/
│   │   └── dow_theory.py           # Algorithmic swing detection and Dow Theory trend classification
│   └── visualization/
│       └── charts.py               # Matplotlib visualization suite
├── tests/
│   ├── test_backtest_engine.py     # Unit tests for execution logic, costs, and lookahead prevention
│   ├── test_indicators.py          # Unit tests for indicator mathematical boundaries
│   ├── test_metrics.py             # Unit tests for financial performance metrics
│   └── test_patterns.py            # Unit tests for candlestick pattern detection geometry
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python package dependencies
└── README.md                       # Project documentation
```

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/technical-trading-research.git
cd technical-trading-research
```

### 2. Set up virtual environment
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Usage Workflow

### 1. Run Test Suite
Validate all indicator formulas, pattern detection rules, and backtesting mechanics:
```bash
pytest
```

### 2. Run Pattern & Statistical Analysis
Detect candlestick patterns, compute indicator series, and generate multi-horizon forward return distributions:
```bash
python scripts/run_pattern_analysis.py
```
*Outputs generated in `data/processed/` and `reports/tables/pattern_forward_return_summary.csv`.*

### 3. Run Backtest Simulation
Execute the baseline multi-indicator strategy and robustness variants against the buy-and-hold benchmark:
```bash
python scripts/run_backtest.py
```
*Outputs generated in `reports/tables/` and `reports/figures/`.*

### 4. Fetch Multi-Year Universe Data (Optional)
To expand research across the 14 constituents of the Nifty FMCG sector (2019–2024):
```bash
python scripts/download_data.py
```

---

## Key Empirical Findings (Case Study: TATACONSUM CY2024)

| Metric | Buy & Hold Benchmark | Multi-Indicator Strategy 1 | Strategy 1b (Robustness Variant) |
|---|---|---|---|
| **Total Return** | **-2.55%** | **0.00%** | **0.00%** |
| **Annualized Volatility** | 18.57% | 0.00% | 0.00% |
| **Sharpe Ratio ($r_f=6.5\%$)** | **-0.38** | n/a | n/a |
| **Max Drawdown** | **-21.76%** | **0.00%** | **0.00%** |
| **Number of Trades** | — | **0** | **0** |
| **Capital Preservation** | Suffered -21.8% DD | 100% Cash Preserved | 100% Cash Preserved |

### Core Insights:
1. **Indicator Conflict During Corrections**: The baseline strategy ($RSI < 40$ oversold trigger + MACD bullish cross + $Close > SMA(50)$ trend filter) generated zero trades because oversold RSI pullbacks occurred exclusively while the price was trading below the 50-day SMA. The trend filter successfully protected capital from the asset's -21.76% maximum drawdown.
2. **Candlestick Reliability**: Across 90 detected pattern instances, textbook directional expectations were frequently violated over small samples (e.g., Shooting Star delivered positive 5-day forward returns). All pattern categories had $n < 20$, highlighting the critical necessity of multi-year cross-sectional sample sizes before claiming a tradable statistical edge.

For full empirical analysis and methodology discussions, see [reports/final_report.md](reports/final_report.md).

---

## License

This project is licensed under the MIT License.
