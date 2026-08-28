from __future__ import annotations

import pandas as pd


# Identify swing highs and swing lows using a rolling window
def find_swing_points(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    highs = df["High"]
    lows = df["Low"]
    roll_max = highs.rolling(window=2 * window + 1, center=True).max()
    roll_min = lows.rolling(window=2 * window + 1, center=True).min()
    swing_high = highs == roll_max
    swing_low = lows == roll_min
    out = pd.DataFrame({"swing_high": swing_high.fillna(False), "swing_low": swing_low.fillna(False)}, index=df.index)
    return out


# Classify trend as uptrend, downtrend, or sideways based on swing points
def classify_trend_from_swings(df: pd.DataFrame, window: int = 5) -> pd.Series:
    swings = find_swing_points(df, window=window)
    highs_seq = df.loc[swings["swing_high"], "High"]
    lows_seq = df.loc[swings["swing_low"], "Low"]

    trend = pd.Series("sideways", index=df.index, dtype=object)

    last_two_highs = []
    last_two_lows = []
    state = "sideways"
    swing_dates = sorted(set(highs_seq.index) | set(lows_seq.index))
    state_at_date = {}
    for d in swing_dates:
        if d in highs_seq.index:
            last_two_highs.append(highs_seq[d])
            last_two_highs = last_two_highs[-2:]
        if d in lows_seq.index:
            last_two_lows.append(lows_seq[d])
            last_two_lows = last_two_lows[-2:]

        higher_high = len(last_two_highs) == 2 and last_two_highs[-1] > last_two_highs[-2]
        higher_low = len(last_two_lows) == 2 and last_two_lows[-1] > last_two_lows[-2]
        lower_high = len(last_two_highs) == 2 and last_two_highs[-1] < last_two_highs[-2]
        lower_low = len(last_two_lows) == 2 and last_two_lows[-1] < last_two_lows[-2]

        if higher_high and higher_low:
            state = "uptrend"
        elif lower_high and lower_low:
            state = "downtrend"
        else:
            state = "sideways"
        state_at_date[d] = state

    trend = trend.astype(object)
    current = "sideways"
    for date in df.index:
        if date in state_at_date:
            current = state_at_date[date]
        trend.loc[date] = current
    return trend


# Generate trend signal based on moving average crossover
def sma_cross_signal(close: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    sma_fast = close.rolling(fast, min_periods=fast).mean()
    sma_slow = close.rolling(slow, min_periods=slow).mean()
    out = pd.Series("undefined", index=close.index, dtype=object)
    out[sma_fast > sma_slow] = "bullish"
    out[sma_fast < sma_slow] = "bearish"
    return out
