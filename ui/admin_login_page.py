# ui/admin_login_page.py (Final Version)

import streamlit as st
import os

def render():
    """
    Renders the administrator login page.
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.header("👑 Administrator Login")
        st.write("Please enter the admin password to access the dashboard.")
        
        with st.form("admin_login_form"):
            admin_pass = st.text_input(
                "Admin Password", 
                type="password", 
                label_visibility="collapsed", 
                placeholder="Admin Password"
            )
            
            submitted = st.form_submit_button("Login to Admin Dashboard", use_container_width=True)

            if submitted:
                # Fetch the correct password from environment variables for security.
                correct_password = os.getenv("ADMIN_PASSWORD", "teacher123")
                
                if admin_pass == correct_password:
                    st.toast("✅ Login successful! Loading dashboard...", icon="🎉")
                    # Store the password in session state to signify a logged-in admin.
                    st.session_state.admin_password = admin_pass
                    st.rerun() # Rerun the script. The router in app.py will detect the new state.
                else:
                    st.error("Incorrect admin password. Please try again.")
        
        # A button to easily go back to the student voting kiosk.
        if st.button("Go back to Student Voting Kiosk"):
            st.session_state.page = "login"
            st.rerun()