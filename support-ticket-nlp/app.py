import os
from pathlib import Path

# Run from this project's folder so relative data paths work locally, in Docker and on Streamlit Cloud
os.chdir(Path(__file__).resolve().parent)

import html
import pandas as pd
import streamlit as st
from src.classifier import load
from src.triage import triage

st.set_page_config(page_title="Support Ticket NLP", page_icon="🎫", layout="wide")
st.title("🎫 Support Ticket Triage — NLP")
st.caption("Classification + entity extraction + priority + routing · synthetic IT support tickets")


@st.cache_resource
def get_model():
    return load()


model, meta = get_model()
COLOURS = {"TICKET_ID": "#264653", "INVOICE": "#2A9D8F", "ACCOUNT": "#8AB17D", "ERROR_CODE": "#E76F51",
           "IP_ADDRESS": "#6D597A", "EMAIL": "#457B9D", "PRODUCT": "#FF3B3B"}


def highlight(text, entities):
    out, pos = [], 0
    for e in entities:
        if e["start"] < pos:
            continue
        out.append(html.escape(text[pos:e["start"]]))
        out.append(f'<span style="background:{COLOURS[e["label"]]};color:white;padding:2px 6px;border-radius:6px">'
                   f'{html.escape(e["text"])} <small>{e["label"]}</small></span>')
        pos = e["end"]
    out.append(html.escape(text[pos:]))
    return "".join(out)


tab1, tab2, tab3 = st.tabs(["Triage a ticket", "Batch triage", "Model performance"])
with tab1:
    text = st.text_area("Ticket text", "Urgent: Outlook crashes with error E512 on startup. Ticket INC204211, "
                                       "contact me at priya@example.com", height=110)
    if text.strip():
        t = triage(text, model)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Category", t["category"])
        c2.metric("Confidence", f"{t['confidence']:.0%}")
        c3.metric("Priority", t["priority"])
        c4.metric("Route to", t["team"])
        st.markdown(highlight(text, t["entities"]), unsafe_allow_html=True)
        st.bar_chart(pd.Series(t["probabilities"]))
with tab2:
    up = st.file_uploader("CSV with a 'text' column", type="csv")
    if up:
        df = pd.read_csv(up)
        res = pd.DataFrame([{k: v for k, v in triage(x, model).items() if k not in ("entities", "probabilities")}
                            for x in df["text"].astype(str)])
        out = pd.concat([df, res], axis=1)
        st.dataframe(out, hide_index=True)
        st.download_button("Download triaged tickets", out.to_csv(index=False), "triaged_tickets.csv")
with tab3:
    st.metric("Macro-F1 (held-out)", meta["macro_f1"])
    st.dataframe(pd.DataFrame(meta["report"]).T)
    st.caption("Training labels include about 6% deliberate noise to mimic real-world mislabelled tickets.")
