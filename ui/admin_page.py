# ui/admin_page.py (Fully Updated and Corrected)

import streamlit as st
from ui.api import get_election_settings

# Import the render functions from all our tab files
from ui.admin_tabs import (
    _1_results_stats_tab,
    _2_election_settings_tab,
    _3_candidate_management_tab,
    _4_student_roster_tab,
    _5_audit_log_tab
)

def render():
    """
    Renders the main administrator dashboard container. This version correctly passes
    the settings object to all tabs that require it.
    """
    # --- Sidebar with Logout Functionality ---
    with st.sidebar:
        st.header("Admin Panel")
        st.write("Welcome, Administrator.")
        
        if st.button("Log Out and Go to Student Kiosk", use_container_width=True, type="primary"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    st.title("Administrator Dashboard")
    password = st.session_state.admin_password

    # --- Fetch Global Settings Once ---
    @st.cache_data(ttl=10)
    def fetch_settings():
        return get_election_settings()

    settings = fetch_settings()

    if not settings:
        st.error("Could not load election settings from the backend. Please ensure the server is running and refresh.")
        return

    # --- Create the main tabs container ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Live Results & Stats", 
        "⚙️ Election Settings", 
        "👥 Candidate Management", 
        "🧑‍🎓 Student Roster",
        "📜 Audit Log"
    ])

    # --- Render Each Tab Module ---
    with tab1:
        _1_results_stats_tab.render(password)

    with tab2:
        _2_election_settings_tab.render(settings, password)

    with tab3:
        _3_candidate_management_tab.render(settings, password)

    with tab4:
        # FIXED: Pass the 'settings' object to the student roster tab as well.
        _4_student_roster_tab.render(settings, password)

    with tab5:
        _5_audit_log_tab.render(password)