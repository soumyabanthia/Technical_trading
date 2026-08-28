from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

PATTERN_MARKER_STYLE = {
    "doji": ("o", "gray"),
    "hammer": ("^", "green"),
    "shooting_star": ("v", "red"),
    "bullish_engulfing": ("^", "darkgreen"),
    "bearish_engulfing": ("v", "darkred"),
    "morning_star": ("*", "blue"),
    "evening_star": ("*", "orange"),
    "three_white_soldiers": ("s", "purple"),
}


# Plot price chart with detected candlestick pattern markers
def plot_price_with_patterns(df: pd.DataFrame, patterns_long: pd.DataFrame, out_path: str | Path, title: str):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df.index, df["Close"], color="black", linewidth=1, label="Close")

    for pattern, (marker, color) in PATTERN_MARKER_STYLE.items():
        subset = patterns_long[patterns_long["pattern"] == pattern]
        if subset.empty:
            continue
        dates = subset["Date"]
        prices = df.loc[df.index.isin(dates), "Close"]
        ax.scatter(prices.index, prices.values, marker=marker, color=color, s=70, label=pattern, zorder=5)

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (₹)")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# Plot price series with swing points and trend shading
def plot_price_with_trend(df: pd.DataFrame, swings: pd.DataFrame, trend: pd.Series, out_path: str | Path, title: str):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df.index, df["Close"], color="black", linewidth=1, label="Close")

    sh = df.loc[swings["swing_high"]]
    sl = df.loc[swings["swing_low"]]
    ax.scatter(sh.index, sh["High"], marker="v", color="red", s=40, label="Swing High", zorder=5)
    ax.scatter(sl.index, sl["Low"], marker="^", color="green", s=40, label="Swing Low", zorder=5)

    colors = {"uptrend": "#d4f4dd", "downtrend": "#f9d6d5", "sideways": "#eeeeee"}
    prev_date = df.index[0]
    prev_state = trend.iloc[0]
    for date, state in trend.items():
        if state != prev_state:
            ax.axvspan(prev_date, date, color=colors.get(prev_state, "white"), alpha=0.5)
            prev_date, prev_state = date, state
    ax.axvspan(prev_date, df.index[-1], color=colors.get(prev_state, "white"), alpha=0.5)

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (₹)")
    ax.legend(loc="upper left", fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# Plot price with SMA overlays and RSI and MACD subplots
def plot_indicator_panel(df: pd.DataFrame, out_path: str | Path, title: str):
    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    axes[0].plot(df.index, df["Close"], color="black", label="Close")
    axes[0].plot(df.index, df["SMA_20"], color="tab:blue", label="SMA 20", linewidth=1)
    axes[0].plot(df.index, df["SMA_50"], color="tab:orange", label="SMA 50", linewidth=1)
    axes[0].set_ylabel("Price (₹)")
    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].set_title(title)

    axes[1].plot(df.index, df["RSI_14"], color="purple")
    axes[1].axhline(70, color="red", linestyle="--", linewidth=0.8)
    axes[1].axhline(30, color="green", linestyle="--", linewidth=0.8)
    axes[1].set_ylabel("RSI(14)")
    axes[1].set_ylim(0, 100)

    axes[2].plot(df.index, df["MACD"], color="tab:blue", label="MACD")
    axes[2].plot(df.index, df["MACD_signal"], color="tab:orange", label="Signal")
    axes[2].bar(df.index, df["MACD_hist"], color="gray", alpha=0.4, width=1.0, label="Histogram")
    axes[2].axhline(0, color="black", linewidth=0.6)
    axes[2].set_ylabel("MACD")
    axes[2].legend(loc="upper left", fontsize=8)
    axes[2].set_xlabel("Date")
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# Plot comparison of equity curves
def plot_equity_curves(curves: dict[str, pd.Series], out_path: str | Path, title: str):
    fig, ax = plt.subplots(figsize=(14, 6))
    for label, curve in curves.items():
        ax.plot(curve.index, curve.values, label=label, linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value (₹)")
    ax.legend(loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# Plot underwater drawdown chart
def plot_drawdown(equity_curve: pd.Series, out_path: str | Path, title: str):
    from src.backtest.metrics import drawdown_series

    dd = drawdown_series(equity_curve)
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.fill_between(dd.index, dd.values * 100, 0, color="red", alpha=0.4)
    ax.plot(dd.index, dd.values * 100, color="darkred", linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


# Plot forward return bar chart grouped by pattern
def plot_forward_return_distribution(summary_df: pd.DataFrame, out_path: str | Path, title: str):
    fig, ax = plt.subplots(figsize=(12, 6))
    df = summary_df.dropna(subset=["mean_ret"]).sort_values("mean_ret")
    colors = ["green" if v > 0 else "red" for v in df["mean_ret"]]
    ax.barh(df["pattern"] + " (h=" + df["horizon"].astype(str) + ")", df["mean_ret"] * 100, color=colors)
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row["mean_ret"] * 100, i, f"  n={int(row['n'])}", va="center", fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Mean forward return (%)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
