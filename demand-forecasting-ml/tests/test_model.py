import pandas as pd
import pytest
from src.features import make_features
from src.model import train_evaluate

sales = pd.read_csv("data/sales.csv")


@pytest.mark.parametrize("product", sales["product"].unique())
def test_model_beats_seasonal_naive(product):
    results, _, _ = train_evaluate(sales, product)
    assert results.loc["Gradient boosting", "MAE"] < results.loc["Seasonal naive (last week)", "MAE"]


def test_no_future_leakage():
    df = make_features(sales[sales["product"] == sales["product"].iloc[0]])
    raw = sales[sales["product"] == sales["product"].iloc[0]].reset_index(drop=True)
    row = df.iloc[0]
    idx = raw.index[pd.to_datetime(raw["date"]) == row["date"]][0]
    assert row["lag_1"] == raw.loc[idx - 1, "units_sold"]
