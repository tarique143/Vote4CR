# app.py (Fully Updated, Complete, and Corrected for Caching Error)

import streamlit as st
from ui import login_page, student_page, admin_page, admin_login_page
from ui.api import get_election_settings, API_URL

# --- Page Configuration (MUST BE THE FIRST AND ONLY CALL) ---
st.set_page_config(
    page_title="E-Voting Platform",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="auto" # "auto" lets pages with sidebars show them.
)

# --- Session State Initialization ---
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'api_url' not in st.session_state:
    st.session_state.api_url = API_URL

# --- Main Application Logic ---

@st.cache_data(ttl=10) # Cache settings for 10 seconds
def fetch_global_settings():
    """
    Fetches all global settings once. This function is now cache-safe
    because the underlying api.py functions no longer call st.toast.
    """
    return get_election_settings()

settings = fetch_global_settings()

# --- NEW: Improved Error Handling (outside the cached function) ---
# This is the correct place to handle UI feedback for failed API calls.
if not settings:
    st.error("🔴 FATAL: Could not connect to the backend server. The application cannot start. Please contact the administrator or refresh the page.")
    # We use st.stop() to halt the execution of the rest of the app if the backend is down.
    st.stop()

# --- Main App Router ---
if 'admin_password' in st.session_state and st.session_state.admin_password:
    # If an admin is logged in, we only render the admin page.
    # The admin_page itself is responsible for rendering its own sidebar and content.
    admin_page.render()
else:
    # For all other pages (login, student voting), the sidebar will be auto-collapsed.
    if st.session_state.page == "student_vote":
        student_page.render(settings)
    elif st.session_state.page == "admin_login":
        admin_login_page.render()
    else:
        st.session_state.page = "login"
        
        if st.button("👑 Admin Login"):
            st.session_state.page = 'admin_login'
            st.rerun()
        
        login_page.render(settings)
