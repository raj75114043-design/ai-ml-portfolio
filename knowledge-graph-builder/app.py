import os
from pathlib import Path

# Run from this project's folder so relative data paths work locally, in Docker and on Streamlit Cloud
os.chdir(Path(__file__).resolve().parent)

import pandas as pd
import streamlit as st
from src.builder import build, to_cypher

st.set_page_config(page_title="Knowledge Graph Builder", page_icon="🕸️", layout="wide")
st.title("🕸️ Knowledge Graph Builder")
st.caption("Ontology · fuzzy entity resolution · schema validation · Neo4j export · synthetic data")

g, review = build()
c1, c2, c3 = st.columns(3)
c1.metric("Nodes", g.number_of_nodes())
c2.metric("Relationships", g.number_of_edges())
c3.metric("Matches for manual review", len(review))

COLOURS = {"Site": "#FF3B3B", "Activity": "#E76F51", "Material": "#2A9D8F", "Vendor": "#264653"}
dot = ['digraph G { rankdir=LR; node [style="filled,rounded", shape=box, fontcolor=white, fontname=Helvetica];']
for n, d in g.nodes(data=True):
    dot.append(f'"{n}" [label="{d["label"]}\\n{d["name"]}", fillcolor="{COLOURS[d["label"]]}"];')
for u, v, d in g.edges(data=True):
    dot.append(f'"{u}" -> "{v}" [label="{d["type"]}", fontsize=9];')
dot.append("}")
st.graphviz_chart("\n".join(dot))

st.subheader("Multi-hop query")
sites = sorted(n for n, d in g.nodes(data=True) if d["label"] == "Site")
site = st.selectbox("Site", sites)
rows = []
for act in g.successors(site):
    for mat in g.successors(act):
        for ven in g.successors(mat):
            rows.append({"Site": site, "Activity": g.nodes[act]["name"], "Status": g.nodes[act]["status"],
                         "Material": g.nodes[mat]["name"], "Vendor": g.nodes[ven]["name"]})
st.dataframe(pd.DataFrame(rows), hide_index=True)

st.subheader("Entity resolution")
er = [{"Material": u, "Source vendor name": d["source_name"], "Resolved to": g.nodes[v]["name"],
       "Confidence": d["confidence"]} for u, v, d in g.edges(data=True) if d["type"] == "SUPPLIED_BY"]
st.dataframe(pd.DataFrame(er), hide_index=True)

st.download_button("Download Neo4j Cypher script", "\n".join(s + ";" for s in to_cypher(g)), "load_graph.cypher")
