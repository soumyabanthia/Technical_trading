import pandas as pd
import numpy as np
import pytest

from src.backtest import metrics


# Test total return calculation
def test_total_return_simple():
    curve = pd.Series([100, 110, 121], index=pd.date_range("2024-01-01", periods=3))
    assert metrics.total_return(curve) == pytest.approx(0.21)


# Test maximum drawdown peak to trough calculation
def test_max_drawdown_detects_peak_to_trough():
    curve = pd.Series([100, 120, 90, 130], index=pd.date_range("2024-01-01", periods=4))
    assert metrics.max_drawdown(curve) == pytest.approx(-0.25)


# Test maximum drawdown is zero for strictly rising series
def test_max_drawdown_zero_for_monotonic_increase():
    curve = pd.Series([100, 105, 110, 120], index=pd.date_range("2024-01-01", periods=4))
    assert metrics.max_drawdown(curve) == pytest.approx(0.0)


# Test compound annual growth rate calculation
def test_cagr_one_year_matches_total_return():
    dates = pd.date_range("2024-01-01", periods=2, freq="365D")
    curve = pd.Series([100, 150], index=dates)
    assert metrics.cagr(curve) == pytest.approx(0.5, abs=1e-2)


# Test win rate and profit factor calculations
def test_trade_stats_win_rate_and_profit_factor():
    trades_df = pd.DataFrame(
        {
            "return_pct": [0.10, -0.05, 0.20, -0.10],
            "holding_days": [5, 3, 10, 2],
        }
    )
    stats = metrics.trade_stats(trades_df)
    assert stats["n_trades"] == 4
    assert stats["win_rate"] == pytest.approx(0.5)
    assert stats["profit_factor"] == pytest.approx(2.0)


# Test trade stats on empty dataframe
def test_trade_stats_handles_no_trades():
    trades_df = pd.DataFrame(columns=["return_pct", "holding_days"])
    stats = metrics.trade_stats(trades_df)
    assert stats["n_trades"] == 0
