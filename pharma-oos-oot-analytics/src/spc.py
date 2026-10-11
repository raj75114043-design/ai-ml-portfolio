"""Statistical process control for batch release data.

OOS  = result outside registered specification limits (formal investigation required).
OOT  = result within specification but statistically unusual against the process history
       (Western Electric / Nelson-style trend rules).
"""
import numpy as np
import pandas as pd

SPECS = {"assay_pct": (95.0, 105.0), "dissolution_pct": (80.0, None)}


def control_limits(series: pd.Series, baseline: int = 30):
    base = series.iloc[:baseline]
    mean = base.mean()
    sigma = base.diff().abs().mean() / 1.128  # moving-range estimate
    return mean, sigma


def oos_flags(df, col):
    lo, hi = SPECS[col]
    flag = pd.Series(False, index=df.index)
    if lo is not None:
        flag |= df[col] < lo
    if hi is not None:
        flag |= df[col] > hi
    return flag


def oot_flags(series: pd.Series, mean: float, sigma: float) -> pd.DataFrame:
    z = (series - mean) / sigma
    rules = pd.DataFrame(index=series.index)
    rules["rule1_beyond_3sigma"] = z.abs() > 3
    above, below = (z > 2).astype(int), (z < -2).astype(int)
    rules["rule2_2of3_beyond_2sigma"] = (above.rolling(3).sum() >= 2) | (below.rolling(3).sum() >= 2)
    side = np.sign(z)
    rules["rule4_8_same_side"] = side.rolling(8).apply(lambda s: abs(s.sum()) == 8, raw=True).fillna(0).astype(bool)
    diffs = np.sign(series.diff())
    rules["rule5_6_trending"] = diffs.rolling(5).apply(lambda s: abs(s.sum()) == 5, raw=True).fillna(0).astype(bool)
    return rules


def cpk(series, lo, hi):
    mu, sd = series.mean(), series.std(ddof=1)
    parts = [x for x in [(hi - mu) / (3 * sd) if hi else None, (mu - lo) / (3 * sd) if lo else None] if x is not None]
    return round(min(parts), 2)
