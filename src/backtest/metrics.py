from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE_ANNUAL = 0.065


# Calculate daily percentage returns
def daily_returns(equity_curve: pd.Series) -> pd.Series:
    return equity_curve.pct_change().dropna()


# Calculate total strategy return
def total_return(equity_curve: pd.Series) -> float:
    return equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0


# Calculate compound annual growth rate
def cagr(equity_curve: pd.Series) -> float:
    n_days = (equity_curve.index[-1] - equity_curve.index[0]).days
    years = n_days / 365.25
    if years <= 0:
        return np.nan
    return (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1 / years) - 1.0


# Calculate annualized return volatility
def annualized_volatility(equity_curve: pd.Series) -> float:
    r = daily_returns(equity_curve)
    return r.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)


# Calculate annualized Sharpe ratio
def sharpe_ratio(equity_curve: pd.Series, risk_free_annual: float = RISK_FREE_RATE_ANNUAL) -> float:
    r = daily_returns(equity_curve)
    rf_daily = (1 + risk_free_annual) ** (1 / TRADING_DAYS_PER_YEAR) - 1
    excess = r - rf_daily
    std = excess.std(ddof=1)
    if std == 0 or np.isnan(std):
        return np.nan
    return (excess.mean() / std) * np.sqrt(TRADING_DAYS_PER_YEAR)


# Calculate Sortino ratio using downside standard deviation
def sortino_ratio(equity_curve: pd.Series, risk_free_annual: float = RISK_FREE_RATE_ANNUAL) -> float:
    r = daily_returns(equity_curve)
    rf_daily = (1 + risk_free_annual) ** (1 / TRADING_DAYS_PER_YEAR) - 1
    excess = r - rf_daily
    downside = excess[excess < 0]
    downside_std = downside.std(ddof=1)
    if downside_std == 0 or np.isnan(downside_std):
        return np.nan
    return (excess.mean() / downside_std) * np.sqrt(TRADING_DAYS_PER_YEAR)


# Calculate maximum drawdown
def max_drawdown(equity_curve: pd.Series) -> float:
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1.0
    return drawdown.min()


# Calculate drawdown series from peak equity
def drawdown_series(equity_curve: pd.Series) -> pd.Series:
    running_max = equity_curve.cummax()
    return equity_curve / running_max - 1.0


# Calculate Calmar ratio
def calmar_ratio(equity_curve: pd.Series) -> float:
    mdd = max_drawdown(equity_curve)
    if mdd == 0:
        return np.nan
    return cagr(equity_curve) / abs(mdd)


# Compute trade performance statistics
def trade_stats(trades_df: pd.DataFrame) -> dict:
    closed = trades_df.dropna(subset=["return_pct"])
    n = len(closed)
    if n == 0:
        return {"n_trades": 0}

    wins = closed[closed["return_pct"] > 0]["return_pct"]
    losses = closed[closed["return_pct"] <= 0]["return_pct"]
    win_rate = len(wins) / n
    avg_win = wins.mean() if len(wins) else np.nan
    avg_loss = losses.mean() if len(losses) else np.nan
    gross_profit = wins.sum() if len(wins) else 0.0
    gross_loss = -losses.sum() if len(losses) else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.nan
    expectancy = closed["return_pct"].mean()

    return {
        "n_trades": n,
        "win_rate": win_rate,
        "avg_trade_return": closed["return_pct"].mean(),
        "median_trade_return": closed["return_pct"].median(),
        "avg_winning_trade": avg_win,
        "avg_losing_trade": avg_loss,
        "best_trade": closed["return_pct"].max(),
        "worst_trade": closed["return_pct"].min(),
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "avg_holding_days": closed["holding_days"].mean(),
    }


# Generate complete metrics report from equity curve and trades
def full_report(equity_curve: pd.Series, trades_df: pd.DataFrame) -> dict:
    report = {
        "total_return": total_return(equity_curve),
        "cagr": cagr(equity_curve),
        "annualized_volatility": annualized_volatility(equity_curve),
        "sharpe_ratio": sharpe_ratio(equity_curve),
        "sortino_ratio": sortino_ratio(equity_curve),
        "max_drawdown": max_drawdown(equity_curve),
        "calmar_ratio": calmar_ratio(equity_curve),
    }
    report.update(trade_stats(trades_df))
    return report
