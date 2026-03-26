"""
Simple session-state login for the TDM Streamlit app.
Mirrors the demo accounts used in the Next.js frontend.
"""

import streamlit as st

_DEMO_USERS = {
    "admin":    {"password": "admin123",  "role": "Admin",     "name": "Admin User"},
    "analyst":  {"password": "analyst123","role": "Analyst",   "name": "Data Analyst"},
    "engineer": {"password": "eng123",    "role": "Engineer",  "name": "Data Engineer"},
}


def login_form() -> None:
    """Render a login form and set st.session_state['user'] on success."""
    st.title("TDM Platform — Deckers Brands")
    st.subheader("Sign in")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")
    if submitted:
        user = _DEMO_USERS.get(username)
        if user and user["password"] == password:
            st.session_state["user"] = {
                "username": username,
                "name":     user["name"],
                "role":     user["role"],
            }
            st.rerun()
        else:
            st.error("Invalid credentials. Try admin/admin123, analyst/analyst123, or engineer/eng123.")


def require_login() -> dict:
    """Return the logged-in user dict; show login form and stop if not logged in."""
    if "user" not in st.session_state:
        login_form()
        st.stop()
    return st.session_state["user"]


def logout() -> None:
    st.session_state.pop("user", None)
    st.rerun()
