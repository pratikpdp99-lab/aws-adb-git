"""Data Requests — submit and track test data requests."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from lib.auth import require_login
from lib.api_client import list_requests, create_request, approve_request

st.set_page_config(page_title="Requests | TDM", layout="wide")
user = require_login()

st.title("📋 Data Requests")

tab_submit, tab_list = st.tabs(["Submit Request", "View All Requests"])

# ── Submit tab ─────────────────────────────────────────────────────────────────
with tab_submit:
    st.subheader("Submit a New Test Data Request")
    with st.form("new_request"):
        c1, c2 = st.columns(2)
        domain      = c1.selectbox("Domain", ["customer", "order", "product", "inventory", "loyalty", "payment"])
        environment = c2.selectbox("Environment", ["dev", "staging"])
        row_count   = st.number_input("Row Count", min_value=1, max_value=1_000_000, value=1000, step=100)
        purpose     = st.text_area("Purpose (optional)", placeholder="e.g. Load testing sprint 42")
        submitted   = st.form_submit_button("Submit Request")

    if submitted:
        try:
            result = create_request(
                requester=user["username"],
                domain=domain,
                environment=environment,
                row_count=row_count,
                purpose=purpose or None,
            )
            st.success(f"Request created: **{result['id']}** (status: {result['status']})")
        except Exception as e:
            st.error(f"Failed to create request: {e}")

# ── List tab ───────────────────────────────────────────────────────────────────
with tab_list:
    st.subheader("All Requests")
    status_filter = st.selectbox("Filter by status", ["All", "PENDING", "APPROVED", "REJECTED", "FULFILLED"])

    try:
        reqs = list_requests(status=None if status_filter == "All" else status_filter)
    except Exception as e:
        st.error(f"Could not load requests: {e}")
        reqs = []

    if reqs:
        df = pd.DataFrame(reqs)[["id", "requester", "domain", "environment", "row_count", "status", "created_at"]]
        df.columns = ["ID", "Requester", "Domain", "Env", "Rows", "Status", "Created"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Approve action (admin only)
        if user["role"] == "Admin":
            st.markdown("---")
            st.subheader("Approve a Request")
            req_id = st.text_input("Request ID to approve", placeholder="REQ-0001")
            if st.button("Approve") and req_id:
                try:
                    result = approve_request(req_id)
                    st.success(f"Request {req_id} approved — new status: {result['status']}")
                except Exception as e:
                    st.error(f"Approval failed: {e}")
    else:
        st.info("No requests found.")

    if st.button("🔄 Refresh"):
        st.rerun()
