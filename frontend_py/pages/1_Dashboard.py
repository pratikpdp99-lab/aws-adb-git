"""Dashboard — KPI cards, recent jobs, and pending requests."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from lib.auth import require_login
from lib.api_client import list_jobs, list_requests, list_datasets
from lib.theme import STATUS_COLORS

st.set_page_config(page_title="Dashboard | TDM", layout="wide")
require_login()

st.title("📊 Dashboard")

# ── Fetch data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def _jobs():
    try:
        return list_jobs(limit=10)
    except Exception:
        return {"runs": [], "total": 0}

@st.cache_data(ttl=30)
def _reqs():
    try:
        return list_requests()
    except Exception:
        return []

@st.cache_data(ttl=60)
def _datasets():
    try:
        return list_datasets()
    except Exception:
        return {"datasets": [], "total": 0}

jobs_data     = _jobs()
requests_data = _reqs()
datasets_data = _datasets()

runs       = jobs_data.get("runs", [])
requests   = requests_data if isinstance(requests_data, list) else []
datasets   = datasets_data.get("datasets", [])

# ── KPI cards ──────────────────────────────────────────────────────────────────
active_jobs      = sum(1 for r in runs if r.get("status") in ("RUNNING", "PENDING"))
pending_requests = sum(1 for r in requests if r.get("status") == "PENDING")
datasets_count   = len(datasets)
# DQ pass rate: naive proxy — SUCCESS jobs / total jobs
total_runs  = len(runs) or 1
passed_runs = sum(1 for r in runs if r.get("status") == "SUCCESS")
dq_rate     = round(passed_runs / total_runs * 100, 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Active Jobs",         active_jobs)
c2.metric("Pending Requests",    pending_requests)
c3.metric("Datasets Available",  datasets_count)
c4.metric("DQ Pass Rate",        f"{dq_rate}%")

st.markdown("---")

# ── Recent jobs ────────────────────────────────────────────────────────────────
st.subheader("Recent Job Runs")

if runs:
    df = pd.DataFrame(runs)[["run_id", "job_name", "status", "trigger", "start_time", "end_time"]]
    df.columns = ["Run ID", "Job Name", "Status", "Trigger", "Start", "End"]

    def _color(val):
        color = STATUS_COLORS.get(val, "#6B7280")
        return f"color: {color}; font-weight: bold"

    styled = df.style.applymap(_color, subset=["Status"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
else:
    st.info("No job runs found. Start the FastAPI backend to see live data.")

# ── Recent requests ────────────────────────────────────────────────────────────
st.subheader("Recent Data Requests")

if requests:
    df_req = pd.DataFrame(requests)[["id", "requester", "domain", "environment", "status", "created_at"]]
    df_req.columns = ["ID", "Requester", "Domain", "Environment", "Status", "Created"]
    st.dataframe(df_req, use_container_width=True, hide_index=True)
else:
    st.info("No data requests yet.")

if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
