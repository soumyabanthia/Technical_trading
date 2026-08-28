import pandas as pd

from src.patterns.candlestick import (
    doji,
    hammer,
    shooting_star,
    bullish_engulfing,
    bearish_engulfing,
    three_white_soldiers,
)


# Helper to build dataframe from row dictionaries
def _df(rows):
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"])


# Test doji detection on tight candle body
def test_doji_detects_tiny_body():
    df = _df([{"Open": 100.0, "High": 105.0, "Low": 95.0, "Close": 100.2}])
    assert doji(df).iloc[0]


# Test doji rejection on wide body
def test_doji_rejects_large_body():
    df = _df([{"Open": 100.0, "High": 110.0, "Low": 95.0, "Close": 108.0}])
    assert not doji(df).iloc[0]


# Test hammer pattern detection
def test_hammer_detects_long_lower_shadow_small_body_near_top():
    df = _df([{"Open": 98.0, "High": 99.0, "Low": 90.0, "Close": 99.0}])
    assert hammer(df).iloc[0]


# Test hammer rejection on tall body
def test_hammer_rejects_long_body():
    df = _df([{"Open": 90.0, "High": 100.0, "Low": 89.0, "Close": 99.0}])
    assert not hammer(df).iloc[0]


# Test shooting star pattern detection
def test_shooting_star_detects_long_upper_shadow_small_body_near_bottom():
    df = _df([{"Open": 100.0, "High": 110.0, "Low": 99.5, "Close": 100.5}])
    assert shooting_star(df).iloc[0]


# Test bullish engulfing pattern detection
def test_bullish_engulfing():
    df = _df(
        [
            {"Open": 100.0, "High": 101.0, "Low": 95.0, "Close": 96.0},
            {"Open": 95.0, "High": 105.0, "Low": 94.0, "Close": 102.0},
        ]
    )
    result = bullish_engulfing(df)
    assert not result.iloc[0]
    assert result.iloc[1]


# Test bearish engulfing pattern detection
def test_bearish_engulfing():
    df = _df(
        [
            {"Open": 96.0, "High": 101.0, "Low": 95.0, "Close": 100.0},
            {"Open": 101.0, "High": 102.0, "Low": 90.0, "Close": 92.0},
        ]
    )
    result = bearish_engulfing(df)
    assert not result.iloc[0]
    assert result.iloc[1]


# Test bullish engulfing requires full body coverage
def test_bullish_engulfing_requires_full_engulf():
    df = _df(
        [
            {"Open": 100.0, "High": 101.0, "Low": 95.0, "Close": 96.0},
            {"Open": 97.0, "High": 99.0, "Low": 96.5, "Close": 98.5},
        ]
    )
    result = bullish_engulfing(df)
    assert not result.iloc[1]


# Test three white soldiers pattern detection
def test_three_white_soldiers_detects_three_rising_bullish_candles():
    df = _df(
        [
            {"Open": 100.0, "High": 105.0, "Low": 99.0, "Close": 104.0},
            {"Open": 101.0, "High": 109.0, "Low": 100.5, "Close": 108.0},
            {"Open": 102.0, "High": 113.0, "Low": 101.5, "Close": 112.0},
        ]
    )
    result = three_white_soldiers(df)
    assert result.iloc[2]


# Test three white soldiers rejection on non-rising closes
def test_three_white_soldiers_rejects_non_monotonic_closes():
    df = _df(
        [
            {"Open": 100.0, "High": 105.0, "Low": 99.0, "Close": 104.0},
            {"Open": 101.0, "High": 109.0, "Low": 100.5, "Close": 108.0},
            {"Open": 102.0, "High": 106.0, "Low": 101.5, "Close": 103.0},
        ]
    )
    result = three_white_soldiers(df)
    assert not result.iloc[2]
