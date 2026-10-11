from pathlib import Path
import streamlit as st
from src.db import init
from src.server import get_site_status, list_sites_by_status, sites_schema

st.set_page_config(page_title="MCP Tool Explorer", page_icon="🔌", layout="wide")
init()
st.title("🔌 MCP Enterprise Server — Tool Explorer")
st.caption("Call the same validated, read-only tools an AI agent would call through the Model Context Protocol")

tool = st.radio("Tool or resource", ["get_site_status", "list_sites_by_status", "schema://sites"], horizontal=True)

if tool == "get_site_status":
    site_id = st.text_input("site_id", "SITE-101")
    st.caption("Try an injection attempt such as `SITE-101; DROP TABLE sites` to see server-side validation.")
    if st.button("Call tool", type="primary"):
        st.json(get_site_status(site_id))
elif tool == "list_sites_by_status":
    status = st.selectbox("status", ["UP", "DOWN", "DEGRADED"])
    limit = st.number_input("limit (capped at 50)", 1, 500, 10)
    if st.button("Call tool", type="primary"):
        st.json(list_sites_by_status(status, int(limit)))
else:
    st.code(sites_schema())

st.subheader("Audit log (latest 10 calls)")
log = Path("audit.log")
st.code("".join(log.read_text().splitlines(True)[-10:]) if log.exists() else "No calls yet.")
