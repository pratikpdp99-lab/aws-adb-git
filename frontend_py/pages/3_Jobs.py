"""Jobs — live Databricks job run status with auto-refresh."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import streamlit as st
import pandas as pd
from lib.auth import require_login
from lib.api_client import list_jobs, trigger_job
from lib.theme import STATUS_COLORS

st.set_page_config(page_title="Jobs | TDM", layout="wide")
require_login()

st.title("⚙️ Job Runs")

# ── Auto-refresh toggle ────────────────────────────────────────────────────────
col_toggle, col_refresh, col_limit = st.columns([2, 1, 1])
auto_refresh = col_toggle.toggle("Auto-refresh every 30s", value=False)
limit        = col_limit.number_input("Limit", min_value=5, max_value=100, value=20, step=5)

if col_refresh.button("🔄 Refresh now"):
    st.rerun()

# ── Fetch ──────────────────────────────────────────────────────────────────────
try:
    data = list_jobs(limit=int(limit))
    runs = data.get("runs", [])
    source = data.get("source", "unknown")
except Exception as e:
    st.error(f"Could not reach backend: {e}")
    runs   = []
    source = "error"

# Source indicator (I — job status sync)
if source == "stub":
    st.warning("⚠️ Showing **stub data** — Databricks credentials not configured.", icon="⚠️")
elif source == "live":
    st.success("✅ Live data from Databricks.", icon="✅")

# ── Status summary ─────────────────────────────────────────────────────────────
if runs:
    counts = {}
    for r in runs:
        s = r.get("status", "UNKNOWN")
        counts[s] = counts.get(s, 0) + 1

    cols = st.columns(len(counts))
    for col, (status, count) in zip(cols, counts.items()):
        color = STATUS_COLORS.get(status, "#6B7280")
        col.markdown(
            f"<div style='text-align:center;padding:8px;border-radius:6px;"
            f"background:{color}22;border:1px solid {color}'>"
            f"<span style='color:{color};font-weight:bold;font-size:1.4em'>{count}</span>"
            f"<br/><span style='color:{color}'>{status}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Runs table ─────────────────────────────────────────────────────────────
    rows = []
    for r in runs:
        status = r.get("status", "")
        color  = STATUS_COLORS.get(status, "#6B7280")
        rows.append({
            "Run ID":    r.get("run_id"),
            "Job Name":  r.get("job_name"),
            "Status":    status,
            "Trigger":   r.get("trigger"),
            "Start":     r.get("start_time", "—"),
            "End":       r.get("end_time", "—"),
            "Error":     r.get("error_message", ""),
        })

    df = pd.DataFrame(rows)

    def _color_status(val):
        c = STATUS_COLORS.get(val, "#6B7280")
        return f"color: {c}; font-weight: bold"

    styled = df.style.applymap(_color_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
else:
    st.info("No job runs available.")

# ── Auto-refresh loop ──────────────────────────────────────────────────────────
if auto_refresh:
    st.caption("⏱ Auto-refreshing in 30 seconds…")
    time.sleep(30)
    st.rerun()
