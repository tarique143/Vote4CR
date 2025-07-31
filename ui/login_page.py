# ui/login_page.py (Fully Updated and Corrected)

import streamlit as st
# FIXED: Removed all API imports except for identify_student, as settings are now passed in.
from ui.api import identify_student
from PIL import Image

def render(settings):
    """
    Renders the student identification page (the main kiosk screen).
    This version is corrected to use the passed-in settings object
    instead of making its own API calls.
    """
    # --- Dynamic Branding ---
    college_info = settings.get("college_info", {})
    college_name = college_info.get("college_name", "E-Voting Kiosk")
    logo_url = college_info.get("college_logo_url")

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        # Use a try-except block to gracefully handle if the URL is invalid or the image is not found
        try:
            st.image(logo_url if logo_url else "assets/default_logo.png", use_container_width=True)
        except Exception:
            st.image("assets/default_logo.png", use_container_width=True)
    
    with col3:
        try:
            st.image(logo_url if logo_url else "assets/default_logo.png", use_container_width=True)
        except Exception:
            st.image("assets/default_logo.png", use_container_width=True)

    with col2:
        st.title(college_name)
        st.header("Student E-Voting Kiosk")
        st.divider()

        st.subheader("Step 1: Identify Yourself to Vote")

        with st.form("student_identify_form"):
            payload = {}
            
            if settings.get("identification_mode") == "name_and_id":
                payload['name'] = st.text_input("Enter Your Full Name", placeholder="As per College Records")

            payload['roll_number'] = st.number_input("Enter Your Roll Number", min_value=1, step=1, format="%d")
            
            # --- Dynamic Stream and Division Logic ---
            academic_structure = settings.get("academic_structure", [])
            if not academic_structure:
                st.warning("No academic streams have been configured by the administrator.")
                st.form_submit_button("Proceed", disabled=True)
                return

            stream_options = [s["stream_name"] for s in academic_structure]
            selected_stream_name = st.selectbox("Select Your Stream", stream_options)
            payload['stream'] = selected_stream_name
            
            selected_stream_config = next((s for s in academic_structure if s["stream_name"] == selected_stream_name), None)
            
            payload['division'] = None
            if selected_stream_config and selected_stream_config["divisions"]:
                payload['division'] = st.selectbox("Select Your Division", selected_stream_config["divisions"])

            submitted = st.form_submit_button("Find Me & Proceed to Vote", use_container_width=True)
            
            if submitted:
                if settings.get("identification_mode") == "name_and_id" and not payload.get('name', '').strip():
                    st.warning("Please enter your full name.")
                elif payload.get('roll_number', 0) <= 0:
                    st.warning("Please enter a valid Roll Number.")
                else:
                    with st.spinner("Verifying your details..."):
                        response = identify_student(payload)
                        if response:
                            data = response
                            st.success(f"Welcome, {data.get('student_name', 'Student')}! Proceeding to vote...")
                            st.session_state.student_identifier = data.get('student_identifier')
                            st.session_state.student_name = data.get('student_name')
                            st.session_state.page = "student_vote"
                            st.rerun()