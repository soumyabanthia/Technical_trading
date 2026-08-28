import numpy as np
import pandas as pd
import pytest

from src.indicators.indicators import sma, ema, rsi, macd, atr


# Test simple moving average calculation
def test_sma_basic():
    s = pd.Series([1, 2, 3, 4, 5])
    result = sma(s, window=3)
    assert np.isnan(result.iloc[0])
    assert np.isnan(result.iloc[1])
    assert result.iloc[2] == pytest.approx(2.0)
    assert result.iloc[4] == pytest.approx(4.0)


# Test exponential moving average convergence
def test_ema_converges_to_constant():
    s = pd.Series([10.0] * 30)
    result = ema(s, span=5)
    assert result.iloc[-1] == pytest.approx(10.0, abs=1e-6)


# Test RSI equals 100 on monotonic price increases
def test_rsi_all_gains_is_100():
    s = pd.Series(np.arange(1, 30, dtype=float))
    result = rsi(s, period=14)
    assert result.iloc[-1] == pytest.approx(100.0, abs=1e-6)


# Test RSI equals 0 on monotonic price decreases
def test_rsi_all_losses_is_0():
    s = pd.Series(np.arange(30, 1, -1, dtype=float))
    result = rsi(s, period=14)
    assert result.iloc[-1] == pytest.approx(0.0, abs=1e-6)


# Test RSI values stay bounded between 0 and 100
def test_rsi_bounded_0_100():
    rng = np.random.default_rng(42)
    s = pd.Series(100 + np.cumsum(rng.normal(0, 1, 200)))
    result = rsi(s, period=14).dropna()
    assert (result >= 0).all() and (result <= 100).all()


# Test MACD dataframe output columns and histogram formula
def test_macd_columns_and_relationship():
    rng = np.random.default_rng(1)
    s = pd.Series(100 + np.cumsum(rng.normal(0, 1, 100)))
    out = macd(s)
    assert set(out.columns) == {"macd", "signal", "hist"}
    diff = (out["macd"] - out["signal"] - out["hist"]).dropna()
    assert (diff.abs() < 1e-9).all()


# Test Average True Range produces non-negative values
def test_atr_non_negative():
    df = pd.DataFrame(
        {
            "High": [10, 11, 12, 11, 13],
            "Low": [9, 9.5, 10, 9, 11],
            "Close": [9.5, 10.5, 11, 10, 12],
        }
    )
    result = atr(df, period=3).dropna()
    assert (result >= 0).all()
