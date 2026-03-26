"""
TDM Platform — Streamlit entry point.
Handles global page config, auth check, and sidebar navigation.
Run: streamlit run frontend_py/app.py
"""

import streamlit as st
import sys
import os

# Allow imports from frontend_py/lib without installing as package
sys.path.insert(0, os.path.dirname(__file__))

from lib.auth import require_login, logout

st.set_page_config(
    page_title="TDM Platform — Deckers",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

user = require_login()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/160x40?text=TDM+Deckers", width=160)
    st.markdown("---")
    st.write(f"**{user['name']}**")
    st.caption(f"Role: {user['role']}")
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        logout()

# ── Landing page ───────────────────────────────────────────────────────────────
st.title("TDM Platform — Deckers Brands")
st.markdown(
    """
    Welcome to the **Test Data Management** platform for Deckers Brands.
    Use the sidebar to navigate between sections.

    | Page | Description |
    |---|---|
    | 📊 Dashboard | KPI overview + recent jobs |
    | 🗂️ Data Catalog | Domain schema + PII + compliance tags |
    | ⚙️ Jobs | Live Databricks job runs |
    | 📋 Requests | Submit and track data requests |
    | 🔍 Compare | Deckers product comparator |
    | 🔒 Security | IAM, connections, red-flag checks |
    | 🔄 E2E Flow | End-to-end pipeline explainer |
    | 🤖 Agents | Catalog + DQ monitoring agents |
    """
)
