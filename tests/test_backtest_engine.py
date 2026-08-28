import pandas as pd
import numpy as np

from src.backtest.engine import run_backtest, buy_and_hold_equity_curve


# Helper to create test dataframe
def _make_df(n=20, start_price=100.0):
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    prices = start_price + np.arange(n, dtype=float)
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": prices + 1,
            "Low": prices - 1,
            "Close": prices,
        },
        index=dates,
    )
    df["buy_signal"] = False
    df["sell_signal"] = False
    return df


# Test that orders execute on the next bar open
def test_no_lookahead_flat_until_execution_bar():
    df = _make_df(n=10)
    df.iloc[2, df.columns.get_loc("buy_signal")] = True
    result = run_backtest(df, initial_capital=100_000, cost_pct=0.0, slippage_pct=0.0, stop_loss_pct=0.99)
    assert result.equity_curve.iloc[2] == 100_000
    assert len(result.trades) >= 1
    assert result.trades[0].entry_date == df.index[3]
    assert result.trades[0].entry_price == df["Open"].iloc[3]


# Test cash balance remains non-negative
def test_cash_never_goes_negative():
    df = _make_df(n=30)
    df.iloc[1, df.columns.get_loc("buy_signal")] = True
    result = run_backtest(df, initial_capital=50_000, cost_pct=0.001, slippage_pct=0.001, stop_loss_pct=0.05)
    assert (result.equity_curve >= 0).all()


# Test that trading costs reduce final equity
def test_transaction_costs_reduce_equity_vs_zero_cost():
    df = _make_df(n=15)
    df.iloc[1, df.columns.get_loc("buy_signal")] = True
    df.iloc[8, df.columns.get_loc("sell_signal")] = True

    no_cost = run_backtest(df.copy(), initial_capital=100_000, cost_pct=0.0, slippage_pct=0.0, stop_loss_pct=0.99)
    with_cost = run_backtest(df.copy(), initial_capital=100_000, cost_pct=0.01, slippage_pct=0.01, stop_loss_pct=0.99)

    assert with_cost.equity_curve.iloc[-1] < no_cost.equity_curve.iloc[-1]


# Test stop loss exit trigger
def test_stop_loss_triggers_and_closes_position():
    n = 20
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    prices = [100] * 3 + [110] + [90] * (n - 4)
    df = pd.DataFrame(
        {"Open": prices, "High": [p + 1 for p in prices], "Low": [p - 1 for p in prices], "Close": prices},
        index=dates,
    )
    df["buy_signal"] = False
    df["sell_signal"] = False
    df.iloc[2, df.columns.get_loc("buy_signal")] = True

    result = run_backtest(df, initial_capital=100_000, cost_pct=0.0, slippage_pct=0.0, stop_loss_pct=0.05)
    assert len(result.trades) >= 1
    assert result.trades[0].exit_reason == "stop_loss"


# Test buy and hold equity calculation
def test_buy_and_hold_matches_simple_calculation():
    df = _make_df(n=10, start_price=100.0)
    curve = buy_and_hold_equity_curve(df, initial_capital=100_000)
    expected_final = 100_000 * (df["Close"].iloc[-1] / df["Open"].iloc[0])
    assert abs(curve.iloc[-1] - expected_final) < 1e-6


# Test position sizing does not exceed available cash
def test_no_position_never_exceeds_available_cash_at_entry():
    df = _make_df(n=10)
    df.iloc[1, df.columns.get_loc("buy_signal")] = True
    result = run_backtest(df, initial_capital=100_000, cost_pct=0.001, slippage_pct=0.001, stop_loss_pct=0.99, risk_fraction=1.0)
    assert result.trades[0].shares * result.trades[0].entry_price <= 100_000 * 1.0001
