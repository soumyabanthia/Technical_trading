from __future__ import annotations

import numpy as np
import pandas as pd


# Compute forward returns for specified horizons
def compute_forward_returns(close: pd.Series, horizons: tuple[int, ...] = (1, 5, 10, 20)) -> pd.DataFrame:
    out = {}
    for h in horizons:
        out[f"fwd_ret_{h}"] = close.shift(-h) / close - 1.0
    return pd.DataFrame(out, index=close.index)


# Summarize forward return statistics per pattern and horizon
def pattern_forward_return_summary(
    patterns_long: pd.DataFrame,
    fwd_returns: pd.DataFrame,
    horizons: tuple[int, ...] = (1, 5, 10, 20),
) -> pd.DataFrame:
    rows = []
    merged = patterns_long.merge(fwd_returns, left_on="Date", right_index=True, how="left")
    for (pattern, direction), grp in merged.groupby(["pattern", "direction"]):
        for h in horizons:
            col = f"fwd_ret_{h}"
            vals = grp[col].dropna()
            n = len(vals)
            if n == 0:
                rows.append(
                    {"pattern": pattern, "direction": direction, "horizon": h, "n": 0}
                )
                continue
            rows.append(
                {
                    "pattern": pattern,
                    "direction": direction,
                    "horizon": h,
                    "n": n,
                    "mean_ret": vals.mean(),
                    "median_ret": vals.median(),
                    "std_ret": vals.std(ddof=1) if n > 1 else np.nan,
                    "pct_positive": (vals > 0).mean(),
                    "min_ret": vals.min(),
                    "max_ret": vals.max(),
                }
            )
    return pd.DataFrame(rows)


MIN_RELIABLE_N = 20


# Flag pattern statistics with low sample size
def flag_low_sample_size(summary: pd.DataFrame, min_n: int = MIN_RELIABLE_N) -> pd.DataFrame:
    out = summary.copy()
    out["low_confidence"] = out["n"] < min_n
    return out
