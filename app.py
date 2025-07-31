# app.py (Fully Updated and Final Version)

import streamlit as st
from ui import login_page, student_page, admin_page, admin_login_page
from ui.api import get_election_settings, API_URL

# --- Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="E-Voting Platform",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- Session State Initialization ---
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'api_url' not in st.session_state:
    st.session_state.api_url = API_URL

# --- Main Application Logic ---

# Fetch all global settings once. This is efficient.
@st.cache_data(ttl=10) # Cache for 10 seconds
def fetch_global_settings():
    return get_election_settings()

settings = fetch_global_settings()

# Halt the app if the backend is down and settings cannot be fetched.
if not settings:
    st.error("FATAL: Could not connect to the backend server. The application cannot start.")
    st.stop()

# --- Main App Router ---

if 'admin_password' in st.session_state and st.session_state.admin_password:
    admin_page.render()
else:
    # Hide the default Streamlit sidebar on non-admin pages.
    st.set_page_config(initial_sidebar_state="collapsed")
    
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