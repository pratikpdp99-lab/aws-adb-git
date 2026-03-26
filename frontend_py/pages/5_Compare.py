"""Deckers Product Comparator — mirrors the /compare page in Next.js."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from lib.auth import require_login
from lib.api_client import list_products, compare_products, get_recommendations

st.set_page_config(page_title="Compare | TDM", layout="wide")
require_login()

st.title("🔍 Deckers Product Compare")

tab_compare, tab_recommend = st.tabs(["Compare Products", "Recommendations"])

# ── Compare tab ────────────────────────────────────────────────────────────────
with tab_compare:
    try:
        catalog = list_products()
        products = catalog.get("products", [])
    except Exception as e:
        st.error(f"Could not load catalog: {e}")
        products = []

    if products:
        options = {f"{p['brand']} — {p['name']} ({p['product_id']})": p["product_id"] for p in products}
        selected = st.multiselect("Select 2–4 products to compare", list(options.keys()), max_selections=4)
        product_ids = [options[s] for s in selected]

        if st.button("Compare", disabled=len(product_ids) < 2):
            try:
                result = compare_products(product_ids)
                st.success(f"**Recommended winner:** {result['recommended_winner']}")
                st.caption(result["recommendation_reason"])

                matrix = pd.DataFrame(result["matrix"])
                # Flatten values dict into columns
                val_df = pd.json_normalize(matrix["values"])
                display = pd.concat([matrix[["attribute", "winner", "winner_reason"]], val_df], axis=1)
                st.dataframe(display, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Compare failed: {e}")
    else:
        st.info("No products available. Start the FastAPI backend.")

# ── Recommendations tab ────────────────────────────────────────────────────────
with tab_recommend:
    st.subheader("Get Personalised Recommendations")
    c1, c2 = st.columns(2)
    activity = c1.selectbox("Activity", ["", "running", "hiking", "casual", "comfort"])
    season   = c2.selectbox("Season",   ["", "spring", "summer", "fall", "winter"])
    c3, c4 = st.columns(2)
    gender   = c3.selectbox("Gender",   ["", "men", "women", "unisex"])
    budget   = c4.number_input("Max Budget ($)", min_value=0, max_value=1000, value=0, step=10)
    segment  = st.selectbox("Customer Segment", ["", "athlete", "outdoor", "casual", "premium"])

    if st.button("Get Recommendations"):
        payload = {}
        if activity: payload["activity"] = activity
        if season:   payload["season"]   = season
        if gender:   payload["gender"]   = gender
        if budget:   payload["budget_max"] = budget
        if segment:  payload["customer_segment"] = segment

        try:
            rec_data = get_recommendations(payload)
            st.caption(rec_data.get("context_summary", ""))
            for rec in rec_data.get("recommendations", []):
                p = rec["product"]
                with st.container():
                    col_info, col_score = st.columns([4, 1])
                    col_info.markdown(
                        f"**{p['brand']} — {p['name']}** (${p['price']:.0f})  \n"
                        f"⭐ {p['rating']} · {p['review_count']:,} reviews"
                    )
                    col_score.metric("Score", f"{rec['score']:.0f}/100")
                    st.caption(" · ".join(rec["match_reasons"][:3]))
                    st.markdown("---")
        except Exception as e:
            st.error(f"Recommendations failed: {e}")
