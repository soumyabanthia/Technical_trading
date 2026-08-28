# Technical Trading Research

A Python project for technical analysis, candlestick pattern detection, and backtesting on daily stock data.

## Features

- Technical indicators: SMA, EMA, RSI, MACD, ATR
- Candlestick pattern detection: Doji, Hammer, Shooting Star, Engulfing patterns, Morning/Evening Star, Three White Soldiers
- Dow Theory trend classification based on swing highs and lows
- Event-driven backtesting engine with next-bar execution, stop losses, and transaction costs
- Performance metrics: Sharpe ratio, Sortino ratio, max drawdown, CAGR, win rate, and profit factor
- Volume confirmation statistics for detected patterns
- Matplotlib charts for prices, indicators, equity curves, and drawdowns

## Project Structure

- `data/`: Raw and processed CSV data files
- `src/`: Source code for indicators, patterns, backtesting, metrics, trend analysis, and charts
- `scripts/`: Scripts to download data, run pattern analysis, and run backtests
- `tests/`: Unit tests for indicators, patterns, and the backtesting engine
- `reports/`: Output figures and summary tables
- `config/`: Configuration parameters

## Setup and Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run tests:

```bash
pytest
```

Run pattern analysis:

```bash
python scripts/run_pattern_analysis.py
```

Run backtest simulation:

```bash
python scripts/run_backtest.py
```

Download additional data via Yahoo Finance (requires internet):

```bash
python scripts/download_data.py
```
