"""Data Catalog — domain cards with schema, PII badges, and compliance tags."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from lib.auth import require_login
from lib.api_client import list_domains

st.set_page_config(page_title="Data Catalog | TDM", layout="wide")
require_login()

st.title("🗂️ Data Catalog")

# ── Filter controls ────────────────────────────────────────────────────────────
col_filter, col_pii = st.columns([3, 1])
search     = col_filter.text_input("Search domains", placeholder="customer, order …")
pii_filter = col_pii.selectbox("PII filter", ["All", "Has PII", "No PII"])

@st.cache_data(ttl=120)
def _domains():
    try:
        return list_domains()
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return {"domains": [], "total": 0}

data    = _domains()
domains = data.get("domains", [])

if pii_filter == "Has PII":
    domains = [d for d in domains if d["pii_fields"]]
elif pii_filter == "No PII":
    domains = [d for d in domains if not d["pii_fields"]]

if search:
    domains = [d for d in domains if search.lower() in d["name"].lower()]

st.caption(f"Showing {len(domains)} domain(s)")

# ── Domain expanders ───────────────────────────────────────────────────────────
for domain in domains:
    has_pii = bool(domain["pii_fields"])
    pii_badge = "🔴 PII" if has_pii else "🟢 No PII"
    header = f"**{domain['name'].upper()}** — {pii_badge} | {domain['estimated_row_count']:,} est. rows"

    with st.expander(header, expanded=False):
        st.caption(domain["description"])
        st.write(f"**Environments:** {', '.join(domain['supported_environments'])}")

        rows = []
        for f in domain["fields"]:
            tags = ", ".join(f.get("compliance_tags", [])) or "—"
            strategy = f.get("masking_strategy") or "—"
            rows.append({
                "Field":             f["name"],
                "Type":              f["type"],
                "PII":               "🔴 Yes" if f["pii"] else "⬜ No",
                "Nullable":          "Yes" if f["nullable"] else "No",
                "Compliance Tags":   tags,
                "Default Masking":   strategy,
            })

        df = pd.DataFrame(rows)

        def _highlight_pii(row):
            if row["PII"] == "🔴 Yes":
                return ["background-color: #FEE2E2"] * len(row)
            return [""] * len(row)

        styled = df.style.apply(_highlight_pii, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)

        if has_pii:
            st.info(f"🔒 PII fields: {', '.join(domain['pii_fields'])}")
