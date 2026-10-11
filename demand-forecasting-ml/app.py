import pandas as pd
import streamlit as st
from src.model import train_evaluate

st.set_page_config(page_title="Demand Forecasting", page_icon="📈", layout="wide")
st.title("📈 Pharma Demand Forecasting")
st.caption("Gradient boosting with lag, rolling and calendar features vs a seasonal-naive baseline · synthetic sales")

sales = pd.read_csv("data/sales.csv")
product = st.sidebar.selectbox("Product", sales["product"].unique())
test_days = st.sidebar.slider("Test window (days)", 30, 180, 90, 15)


@st.cache_data
def run(product, test_days):
    return train_evaluate(sales, product, test_days)


results, test, importance = run(product, test_days)
gain = 1 - results.loc["Gradient boosting", "MAE"] / results.loc["Seasonal naive (last week)", "MAE"]
c1, c2, c3 = st.columns(3)
c1.metric("Model MAE (units/day)", results.loc["Gradient boosting", "MAE"])
c2.metric("Model MAPE", f'{results.loc["Gradient boosting", "MAPE %"]}%')
c3.metric("MAE improvement vs baseline", f"{gain:.0%}")

st.subheader("Actual vs forecast (one-step-ahead backtest)")
st.line_chart(test.set_index("date")[["units_sold", "forecast", "seasonal_naive"]])
left, right = st.columns(2)
left.subheader("Error metrics")
left.dataframe(results)
right.subheader("Forecast drivers (permutation importance)")
right.bar_chart(importance)

with st.expander("History"):
    st.line_chart(sales[sales["product"] == product].set_index("date")["units_sold"])
