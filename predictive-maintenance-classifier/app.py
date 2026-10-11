import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import precision_recall_curve
from src.train import ARTIFACTS, COST_FN, COST_FP, expected_cost, load_split, main as train
from src.api import score, model, meta

st.set_page_config(page_title="Predictive Maintenance", page_icon="⚙️", layout="wide")
st.title("⚙️ Predictive Maintenance — Failure Classifier")
st.caption(f"Imbalanced classification (failure rate {meta['failure_rate']:.1%}) · cost-based threshold · synthetic sensor data")

tab1, tab2 = st.tabs(["Score a machine", "Model performance"])

with tab1:
    c1, c2, c3 = st.columns(3)
    r = {"air_temp_k": c1.slider("Air temperature (K)", 290.0, 310.0, 300.0),
         "process_temp_k": c1.slider("Process temperature (K)", 300.0, 320.0, 310.0),
         "rotational_speed_rpm": c2.slider("Rotational speed (rpm)", 1000.0, 2800.0, 1540.0),
         "torque_nm": c2.slider("Torque (Nm)", 5.0, 80.0, 40.0),
         "tool_wear_min": c3.slider("Tool wear (min)", 0.0, 250.0, 100.0),
         "vibration_mm_s": c3.slider("Vibration (mm/s)", 0.5, 8.0, 3.0)}
    s = score(r)
    colour = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}[s["risk"]]
    st.metric("Failure probability", f"{s['failure_probability']:.1%}", help=f"Decision threshold {s['threshold']}")
    st.markdown(f"### {colour} Risk: {s['risk']} — " + ("schedule maintenance" if s["maintenance_required"] else "no action needed"))

with tab2:
    st.subheader("Model comparison")
    st.dataframe(pd.DataFrame(meta["comparison"]).T)
    _, X_te, _, y_te = load_split()
    proba = model.predict_proba(X_te)[:, 1]
    left, right = st.columns(2)
    with left:
        p, rc, _ = precision_recall_curve(y_te, proba)
        fig, ax = plt.subplots(figsize=(5, 3.6))
        ax.plot(rc, p, color="#FF3B3B")
        ax.axhline(y_te.mean(), ls="--", color="grey", label="No-skill baseline")
        ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.set_title("Precision-Recall curve"); ax.legend()
        st.pyplot(fig)
    with right:
        t = st.slider("Decision threshold", 0.02, 0.95, float(meta["threshold"]), 0.01)
        cost, fn, fp = expected_cost(y_te, proba, t)
        tp = int(((y_te == 1) & (proba >= t)).sum())
        st.write(f"Cost model: missed failure = {COST_FN:,}, false alarm = {COST_FP:,}")
        st.table(pd.DataFrame([[len(y_te) - tp - fn - fp, fp], [fn, tp]],
                              index=["Actual: normal", "Actual: failure"], columns=["Predicted: normal", "Predicted: failure"]))
        st.metric("Expected cost on test set", f"{cost:,}")
        st.metric("Recall (failures caught)", f"{tp / max(tp + fn, 1):.0%}")
