"""
Agents — Catalog Agent + DQ Monitor Agent chat UI.
Calls backend agent endpoints which use the Claude API internally.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from lib.auth import require_login

st.set_page_config(page_title="Agents | TDM", layout="wide")
require_login()

st.title("🤖 TDM Agents")
st.caption("AI-powered catalog Q&A and data quality monitoring.")

tab_catalog, tab_dq = st.tabs(["🗂️ Catalog Agent", "📊 DQ Monitor Agent"])

# ── Catalog Agent ──────────────────────────────────────────────────────────────
with tab_catalog:
    st.markdown("""
    Ask questions about the TDM data catalog:
    - _"What PII fields are in the customer domain?"_
    - _"What compliance tags does the payment domain have?"_
    - _"Show me lineage for order"_
    - _"Which fields are masked in the customer domain?"_
    """)

    if "catalog_history" not in st.session_state:
        st.session_state["catalog_history"] = []

    for msg in st.session_state["catalog_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask the catalog agent…"):
        st.session_state["catalog_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    import requests as _r
                    base = os.getenv("TDM_API_URL", "http://localhost:8000")
                    resp = _r.post(f"{base}/agents/catalog", json={"question": prompt}, timeout=30)
                    resp.raise_for_status()
                    answer = resp.json().get("answer", "No answer returned.")
                except Exception as e:
                    answer = f"❌ Agent error: {e}\n\nMake sure the FastAPI backend is running and `ANTHROPIC_API_KEY` is set."
            st.markdown(answer)
        st.session_state["catalog_history"].append({"role": "assistant", "content": answer})

    if st.button("Clear catalog history"):
        st.session_state["catalog_history"] = []
        st.rerun()

# ── DQ Monitor Agent ───────────────────────────────────────────────────────────
with tab_dq:
    st.markdown("""
    Ask questions about data quality run results:
    - _"Did the last job pass DQ?"_
    - _"What failed in the last run?"_
    - _"Show me DQ results for customer"_
    """)

    if "dq_history" not in st.session_state:
        st.session_state["dq_history"] = []

    for msg in st.session_state["dq_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask the DQ monitor agent…", key="dq_input"):
        st.session_state["dq_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Checking DQ results…"):
                try:
                    import requests as _r
                    base = os.getenv("TDM_API_URL", "http://localhost:8000")
                    resp = _r.post(f"{base}/agents/dq", json={"question": prompt}, timeout=30)
                    resp.raise_for_status()
                    answer = resp.json().get("answer", "No answer returned.")
                except Exception as e:
                    answer = f"❌ Agent error: {e}\n\nMake sure the FastAPI backend is running and `ANTHROPIC_API_KEY` is set."
            st.markdown(answer)
        st.session_state["dq_history"].append({"role": "assistant", "content": answer})

    if st.button("Clear DQ history"):
        st.session_state["dq_history"] = []
        st.rerun()
