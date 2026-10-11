import pandas as pd
from src.model import train_evaluate

sales = pd.read_csv("data/sales.csv")
for product in sales["product"].unique():
    results, _, importance = train_evaluate(sales, product)
    gain = 1 - results.loc["Gradient boosting", "MAE"] / results.loc["Seasonal naive (last week)", "MAE"]
    print(f"{product}  (MAE improvement vs baseline: {gain:.0%})")
    print(results.to_string())
    print("Top drivers:", ", ".join(importance.index[:3]), "\n")
