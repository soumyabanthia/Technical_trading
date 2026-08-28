from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Trade:
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp | None = None
    exit_price: float | None = None
    shares: float = 0.0
    exit_reason: str | None = None

    # Calculate trade percentage return
    @property
    def return_pct(self) -> float | None:
        if self.exit_price is None:
            return None
        return self.exit_price / self.entry_price - 1.0

    # Calculate trade holding duration in days
    @property
    def holding_days(self) -> int | None:
        if self.exit_date is None:
            return None
        return (self.exit_date - self.entry_date).days


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: list[Trade]
    initial_capital: float

    # Convert trades list to dataframe
    @property
    def trades_df(self) -> pd.DataFrame:
        columns = [
            "entry_date", "exit_date", "entry_price", "exit_price",
            "shares", "return_pct", "holding_days", "exit_reason",
        ]
        rows = []
        for t in self.trades:
            rows.append(
                {
                    "entry_date": t.entry_date,
                    "exit_date": t.exit_date,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "shares": t.shares,
                    "return_pct": t.return_pct,
                    "holding_days": t.holding_days,
                    "exit_reason": t.exit_reason,
                }
            )
        if not rows:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(rows)


# Run long-only backtest simulation with trailing stop loss
def run_backtest(
    df: pd.DataFrame,
    initial_capital: float = 1_000_000.0,
    cost_pct: float = 0.0005,
    slippage_pct: float = 0.0005,
    stop_loss_pct: float = 0.05,
    risk_fraction: float = 1.0,
) -> BacktestResult:
    required = {"Open", "High", "Low", "Close", "buy_signal", "sell_signal"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"run_backtest: df missing columns {missing}")

    cash = initial_capital
    shares_held = 0.0
    trades: list[Trade] = []
    open_trade: Trade | None = None
    highest_close_since_entry = None

    equity_curve = pd.Series(index=df.index, dtype=float)
    pending_action: str | None = None

    dates = df.index.to_list()
    for i, date in enumerate(dates):
        row = df.loc[date]

        if pending_action == "buy" and shares_held == 0:
            exec_price = row["Open"] * (1 + slippage_pct)
            capital_to_use = cash * risk_fraction
            shares_held = (capital_to_use * (1 - cost_pct)) / exec_price
            cash -= shares_held * exec_price * (1 + cost_pct)
            open_trade = Trade(entry_date=date, entry_price=exec_price, shares=shares_held)
            highest_close_since_entry = row["Close"]
        elif pending_action == "sell" and shares_held > 0 and open_trade is not None:
            exec_price = row["Open"] * (1 - slippage_pct)
            proceeds = shares_held * exec_price * (1 - cost_pct)
            cash += proceeds
            open_trade.exit_date = date
            open_trade.exit_price = exec_price
            open_trade.exit_reason = open_trade.exit_reason or "signal"
            trades.append(open_trade)
            open_trade = None
            shares_held = 0.0
            highest_close_since_entry = None
        pending_action = None

        equity_curve.loc[date] = cash + shares_held * row["Close"]

        if shares_held > 0:
            highest_close_since_entry = max(highest_close_since_entry, row["Close"])
            stop_price = highest_close_since_entry * (1 - stop_loss_pct)
            if row["Close"] <= stop_price:
                pending_action = "sell"
                if open_trade is not None:
                    open_trade.exit_reason = "stop_loss"
            elif bool(row["sell_signal"]):
                pending_action = "sell"
        else:
            if bool(row["buy_signal"]):
                pending_action = "buy"

    if shares_held > 0 and open_trade is not None:
        last_date = dates[-1]
        last_close = df.loc[last_date, "Close"]
        exec_price = last_close * (1 - slippage_pct)
        proceeds = shares_held * exec_price * (1 - cost_pct)
        cash += proceeds
        open_trade.exit_date = last_date
        open_trade.exit_price = exec_price
        open_trade.exit_reason = "end_of_data"
        trades.append(open_trade)
        equity_curve.loc[last_date] = cash

    return BacktestResult(equity_curve=equity_curve, trades=trades, initial_capital=initial_capital)


# Calculate buy and hold equity curve benchmark
def buy_and_hold_equity_curve(df: pd.DataFrame, initial_capital: float = 1_000_000.0) -> pd.Series:
    entry_price = df["Open"].iloc[0]
    shares = initial_capital / entry_price
    return shares * df["Close"]
