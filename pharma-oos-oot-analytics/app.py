import os
from pathlib import Path

# Run from this project's folder so relative data paths work locally, in Docker and on Streamlit Cloud
os.chdir(Path(__file__).resolve().parent)

import pandas as pd
import streamlit as st
from src.analysis import analyse, control_chart
from src.spc import SPECS

st.set_page_config(page_title="Pharma OOS / OOT Analytics", page_icon="💊", layout="wide")
st.title("💊 Pharma OOS / OOT Analytics")
st.caption("Batch release trending for APQR and CPV · synthetic data · not for GMP decision-making")

uploaded = st.sidebar.file_uploader("Upload batch results CSV", type="csv")
df = pd.read_csv(uploaded) if uploaded else pd.read_csv("data/batch_results.csv")
params = [c for c in SPECS if c in df.columns]
if not params:
    st.error(f"The file must contain at least one of: {', '.join(SPECS)}")
    st.stop()
col = st.sidebar.selectbox("Quality attribute", params)
baseline = st.sidebar.slider("Baseline batches for control limits", 10, max(10, len(df) - 5), min(30, len(df) - 5))

res, stats = analyse(df, col, baseline)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Batches", len(res))
c2.metric("OOS", int(res.OOS.sum()))
c3.metric("OOT", int(res.OOT.sum()))
c4.metric("Cpk", stats["cpk"])

st.pyplot(control_chart(res, col, stats))

left, right = st.columns(2)
with left:
    st.subheader("OOS — formal investigation")
    st.dataframe(res.loc[res.OOS].drop(columns=["OOS", "OOT", "OOT_rules"]), hide_index=True)
with right:
    st.subheader("OOT — trend review")
    st.dataframe(res.loc[res.OOT, [c for c in res.columns if c not in ("OOS", "OOT")]], hide_index=True)

st.download_button("Download flagged batches (CSV)", res.to_csv(index=False), "flagged_batches.csv")
with st.expander("Method"):
    st.markdown("Control limits use the moving-range estimate of sigma from the baseline batches. "
                "OOT rules: one point beyond 3σ; two of three beyond 2σ on one side; eight on one side; "
                "six steadily trending. OOS uses registered specification limits.")
