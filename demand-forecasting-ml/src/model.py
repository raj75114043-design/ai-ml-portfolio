import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from .features import FEATURES, make_features


def metrics(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return {"MAE": round(float(np.mean(np.abs(y - p))), 2),
            "RMSE": round(float(np.sqrt(np.mean((y - p) ** 2))), 2),
            "MAPE %": round(float(np.mean(np.abs(y - p) / np.maximum(y, 1)) * 100), 2)}


SCALED = [f for f in FEATURES if f.startswith(("lag_", "roll_"))]


def _design(df):
    """Scale level-dependent features by the trailing 28-day mean so the model learns relative patterns
    and can follow a growing trend instead of being capped at levels seen in training."""
    X = df[FEATURES].copy()
    scale = df["roll_mean_28"].clip(lower=1)
    X[SCALED] = X[SCALED].div(scale, axis=0)
    return X, scale


def train_evaluate(sales: pd.DataFrame, product: str, test_days: int = 90):
    """Chronological split: train on the past, evaluate one-step-ahead on the final `test_days`."""
    df = make_features(sales[sales["product"] == product])
    cutoff = df["date"].max() - pd.Timedelta(days=test_days)
    train, test = df[df["date"] <= cutoff], df[df["date"] > cutoff]
    model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05,
                                          min_samples_leaf=40, l2_regularization=1.0, random_state=42)
    X_tr, s_tr = _design(train)
    X_te, s_te = _design(test)
    model.fit(X_tr, train["units_sold"] / s_tr)
    test = test.assign(forecast=(model.predict(X_te) * s_te).round(), seasonal_naive=test["lag_7"])
    results = pd.DataFrame({"Seasonal naive (last week)": metrics(test["units_sold"], test["seasonal_naive"]),
                            "Gradient boosting": metrics(test["units_sold"], test["forecast"])}).T
    imp = permutation_importance(model, X_te, test["units_sold"] / s_te, n_repeats=5, random_state=0)
    importance = pd.Series(imp.importances_mean, index=FEATURES).sort_values(ascending=False)
    return results, test[["date", "units_sold", "forecast", "seasonal_naive"]], importance
