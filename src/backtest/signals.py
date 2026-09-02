from __future__ import annotations

import pandas as pd


# Check if MACD crossed above signal line
def macd_cross_up(macd_line: pd.Series, signal_line: pd.Series) -> pd.Series:
    return (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))


# Check if MACD crossed below signal line
def macd_cross_down(macd_line: pd.Series, signal_line: pd.Series) -> pd.Series:
    return (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))


# Generate baseline strategy buy and sell signals
def generate_baseline_signals(
    df: pd.DataFrame,
    rsi_buy_max: float = 40.0,
    rsi_sell_min: float = 65.0,
    confirm_bars: int = 2,
) -> pd.DataFrame:
    out = df.copy()

    cross_up = macd_cross_up(out["MACD"], out["MACD_signal"])
    cross_up_confirmed = cross_up.copy()
    for lag in range(1, confirm_bars):
        cross_up_confirmed &= cross_up.shift(lag, fill_value=False)

    macd_above = out["MACD"] > out["MACD_signal"]
    held_n_bars = macd_above.copy()
    for lag in range(1, confirm_bars):
        held_n_bars &= macd_above.shift(lag, fill_value=False)

    buy = (
        (out["RSI_14"] < rsi_buy_max)
        & held_n_bars
        & (out["Close"] > out["SMA_50"])
    )

    cross_down = macd_cross_down(out["MACD"], out["MACD_signal"])
    sell = (out["RSI_14"] > rsi_sell_min) | (cross_down & (out["Close"] < out["SMA_20"]))

    out["buy_signal"] = buy.fillna(False)
    out["sell_signal"] = sell.fillna(False)
    return out


# Generate relaxed strategy signals for robustness check
def generate_relaxed_signals(
    df: pd.DataFrame,
    rsi_buy_max: float = 45.0,
    rsi_sell_min: float = 60.0,
) -> pd.DataFrame:
    out = df.copy()
    cross_up = macd_cross_up(out["MACD"], out["MACD_signal"])
    cross_down = macd_cross_down(out["MACD"], out["MACD_signal"])

    buy = (out["RSI_14"] < rsi_buy_max) & cross_up & (out["Close"] > out["SMA_50"])
    sell = (out["RSI_14"] > rsi_sell_min) | (cross_down & (out["Close"] < out["SMA_20"]))

    out["buy_signal"] = buy.fillna(False)
    out["sell_signal"] = sell.fillna(False)
    return out
