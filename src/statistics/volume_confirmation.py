from __future__ import annotations

import pandas as pd


# Check if pattern volume exceeds recent rolling average
def add_volume_confirmation(
    patterns_long: pd.DataFrame,
    df: pd.DataFrame,
    volume_multiple: float = 1.2,
    lookback: int = 20,
) -> pd.DataFrame:
    avg_vol_prior = df["Volume"].rolling(lookback, min_periods=lookback).mean().shift(1)
    ref = pd.DataFrame({"avg_vol_prior": avg_vol_prior, "Volume": df["Volume"]}, index=df.index)

    out = patterns_long.merge(ref, left_on="Date", right_index=True, how="left")
    out["volume_confirmed"] = out["Volume"] >= (volume_multiple * out["avg_vol_prior"])
    out["volume_confirmed"] = out["volume_confirmed"].fillna(False)
    return out
