from __future__ import annotations

import pandas as pd


# Calculate candle body size
def _body(df: pd.DataFrame) -> pd.Series:
    return (df["Close"] - df["Open"]).abs()


# Calculate high to low range
def _range(df: pd.DataFrame) -> pd.Series:
    return (df["High"] - df["Low"]).replace(0, pd.NA)


# Calculate upper shadow length
def _upper_shadow(df: pd.DataFrame) -> pd.Series:
    return df["High"] - df[["Open", "Close"]].max(axis=1)


# Calculate lower shadow length
def _lower_shadow(df: pd.DataFrame) -> pd.Series:
    return df[["Open", "Close"]].min(axis=1) - df["Low"]


# Check if candle is bullish
def _is_bullish(df: pd.DataFrame) -> pd.Series:
    return df["Close"] > df["Open"]


# Check if candle is bearish
def _is_bearish(df: pd.DataFrame) -> pd.Series:
    return df["Close"] < df["Open"]


# Detect doji pattern
def doji(df: pd.DataFrame, body_to_range_max: float = 0.05) -> pd.Series:
    rng = _range(df)
    return (_body(df) / rng <= body_to_range_max).fillna(False)


# Detect hammer pattern
def hammer(
    df: pd.DataFrame,
    lower_shadow_min_ratio: float = 2.0,
    upper_shadow_max_ratio: float = 0.3,
    body_max_ratio: float = 0.35,
) -> pd.Series:
    body = _body(df)
    rng = _range(df)
    lower = _lower_shadow(df)
    upper = _upper_shadow(df)
    cond = (
        (body / rng <= body_max_ratio)
        & (lower >= lower_shadow_min_ratio * body.clip(lower=1e-9))
        & (upper <= upper_shadow_max_ratio * rng)
    )
    return cond.fillna(False)


# Detect shooting star pattern
def shooting_star(
    df: pd.DataFrame,
    upper_shadow_min_ratio: float = 2.0,
    lower_shadow_max_ratio: float = 0.3,
    body_max_ratio: float = 0.35,
) -> pd.Series:
    body = _body(df)
    rng = _range(df)
    lower = _lower_shadow(df)
    upper = _upper_shadow(df)
    cond = (
        (body / rng <= body_max_ratio)
        & (upper >= upper_shadow_min_ratio * body.clip(lower=1e-9))
        & (lower <= lower_shadow_max_ratio * rng)
    )
    return cond.fillna(False)


# Detect bullish engulfing pattern
def bullish_engulfing(df: pd.DataFrame) -> pd.Series:
    o, c = df["Open"], df["Close"]
    prev_bearish = _is_bearish(df).shift(1)
    cur_bullish = _is_bullish(df)
    engulfs = (c > o.shift(1)) & (o < c.shift(1))
    return (prev_bearish & cur_bullish & engulfs).fillna(False)


# Detect bearish engulfing pattern
def bearish_engulfing(df: pd.DataFrame) -> pd.Series:
    o, c = df["Open"], df["Close"]
    prev_bullish = _is_bullish(df).shift(1)
    cur_bearish = _is_bearish(df)
    engulfs = (o > c.shift(1)) & (c < o.shift(1))
    return (prev_bullish & cur_bearish & engulfs).fillna(False)


# Detect morning star pattern
def morning_star(df: pd.DataFrame, gap_tolerance: float = 0.0) -> pd.Series:
    body = _body(df)
    day1_bearish = _is_bearish(df).shift(2)
    day1_body = body.shift(2)
    day2_small = (body.shift(1) <= 0.3 * day1_body.clip(lower=1e-9))
    day2_gap_down = df[["Open", "Close"]].max(axis=1).shift(1) <= df["Open"].shift(2) - gap_tolerance
    day3_bullish = _is_bullish(df)
    day1_mid = (df["Open"].shift(2) + df["Close"].shift(2)) / 2
    day3_closes_above_mid = df["Close"] > day1_mid
    return (day1_bearish & day2_small & day3_bullish & day3_closes_above_mid).fillna(False)


# Detect evening star pattern
def evening_star(df: pd.DataFrame, gap_tolerance: float = 0.0) -> pd.Series:
    body = _body(df)
    day1_bullish = _is_bullish(df).shift(2)
    day1_body = body.shift(2)
    day2_small = (body.shift(1) <= 0.3 * day1_body.clip(lower=1e-9))
    day2_gap_up = df[["Open", "Close"]].min(axis=1).shift(1) >= df["Close"].shift(2) + gap_tolerance
    day3_bearish = _is_bearish(df)
    day1_mid = (df["Open"].shift(2) + df["Close"].shift(2)) / 2
    day3_closes_below_mid = df["Close"] < day1_mid
    return (day1_bullish & day2_small & day3_bearish & day3_closes_below_mid).fillna(False)


# Detect three white soldiers pattern
def three_white_soldiers(df: pd.DataFrame, min_body_ratio: float = 0.5) -> pd.Series:
    bullish = _is_bullish(df)
    all_bullish = bullish & bullish.shift(1) & bullish.shift(2)
    higher_closes = (df["Close"] > df["Close"].shift(1)) & (
        df["Close"].shift(1) > df["Close"].shift(2)
    )
    opens_within_prev_body = (
        (df["Open"] > df["Open"].shift(1)) & (df["Open"] < df["Close"].shift(1))
        & (df["Open"].shift(1) > df["Open"].shift(2)) & (df["Open"].shift(1) < df["Close"].shift(2))
    )
    real_bodies = (_body(df) / _range(df) >= min_body_ratio) & (
        _body(df).shift(1) / _range(df).shift(1) >= min_body_ratio
    ) & (_body(df).shift(2) / _range(df).shift(2) >= min_body_ratio)
    return (all_bullish & higher_closes & opens_within_prev_body & real_bodies).fillna(False)


PATTERN_FUNCTIONS = {
    "doji": doji,
    "hammer": hammer,
    "shooting_star": shooting_star,
    "bullish_engulfing": bullish_engulfing,
    "bearish_engulfing": bearish_engulfing,
    "morning_star": morning_star,
    "evening_star": evening_star,
    "three_white_soldiers": three_white_soldiers,
}


# Run all pattern detectors and return long format dataframe
def detect_all_patterns(df: pd.DataFrame) -> pd.DataFrame:
    direction = {
        "doji": "neutral",
        "hammer": "bullish",
        "shooting_star": "bearish",
        "bullish_engulfing": "bullish",
        "bearish_engulfing": "bearish",
        "morning_star": "bullish",
        "evening_star": "bearish",
        "three_white_soldiers": "bullish",
    }
    records = []
    for name, fn in PATTERN_FUNCTIONS.items():
        mask = fn(df)
        for date in df.index[mask]:
            records.append({"Date": date, "pattern": name, "direction": direction[name]})
    return pd.DataFrame(records).sort_values("Date").reset_index(drop=True)
