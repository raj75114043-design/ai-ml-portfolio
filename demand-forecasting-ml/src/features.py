import pandas as pd

LAGS = [1, 7, 14, 28]
FEATURES = [f"lag_{l}" for l in LAGS] + ["roll_mean_7", "roll_mean_28", "roll_std_7",
                                         "day_of_week", "month", "day_of_year", "promotion", "holiday",
                                         "promotion_lag_7", "holiday_lag_7"]


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    """Lag, rolling and calendar features. Rolling windows are shifted so no future data leaks in."""
    df = df.sort_values("date").copy()
    df["date"] = pd.to_datetime(df["date"])
    y = df["units_sold"]
    for l in LAGS:
        df[f"lag_{l}"] = y.shift(l)
    df["roll_mean_7"] = y.shift(1).rolling(7).mean()
    df["roll_mean_28"] = y.shift(1).rolling(28).mean()
    df["roll_std_7"] = y.shift(1).rolling(7).std()
    df["promotion_lag_7"] = df["promotion"].shift(7)
    df["holiday_lag_7"] = df["holiday"].shift(7)
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear
    return df.dropna()
