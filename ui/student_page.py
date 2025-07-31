# ui/student_page.py (Fully Updated and Corrected for Final API Structure)

import streamlit as st
from ui.api import get_candidates, submit_vote
import time

def render(settings):
    """
    Renders the dynamic voting page where the student selects candidates
    for all configured positions. This version is corrected to handle the
    new API response format.
    """

    # --- Security Check ---
    if 'student_identifier' not in st.session_state or st.session_state.student_identifier is None:
        st.session_state.page = "login"
        st.rerun()

    student_name = st.session_state.get('student_name', 'Student')
    student_identifier = st.session_state.student_identifier

    # --- Sidebar Information ---
    with st.sidebar:
        st.header(f"Voting as: {student_name}")
        st.info("Your vote is final and cannot be changed once submitted.")
        if st.button("Cancel and Go Back"):
            st.session_state.page = "login"
            # Clear student data from session state
            if 'student_identifier' in st.session_state:
                del st.session_state.student_identifier
            if 'student_name' in st.session_state:
                del st.session_state.student_name
            st.rerun()

    # --- Main Page Content ---
    st.title("Step 2: Cast Your Vote")

    if settings.get("voting_status") == "CLOSED":
        st.warning("The voting session is currently closed by the administrator.")
        return

    st.success("The voting session is OPEN! Please make your selections below.")
    
    # Fetch all candidates
    all_candidates = get_candidates()
    if not all_candidates:
        st.error("No candidates have been registered for this election yet.")
        return
        
    positions = settings.get("positions", [])
    
    with st.form("vote_form"):
        selections = {} # This dictionary will hold the vote: {'position_id': 'candidate_name'}
        
        # --- Dynamic Ballot Generation ---
        for pos in positions:
            pos_id = pos["id"]
            pos_title = pos["title"]
            
            st.subheader(pos_title)
            
            # Filter candidates for the current position
            candidates_for_pos = [c for c in all_candidates if c.get("position_id") == pos_id]
            
            if not candidates_for_pos:
                st.warning(f"No candidates are running for the position of {pos_title}.")
                continue

            candidate_names = ["-- Select a Candidate --"] + [c["name"] for c in candidates_for_pos]
            candidate_photos = {c["name"]: c.get("photo_url") for c in candidates_for_pos}
            
            selected_candidate = st.radio(
                f"Select your candidate for {pos_title}",
                options=candidate_names,
                horizontal=True,
                label_visibility="collapsed"
            )

            if selected_candidate and selected_candidate != "-- Select a Candidate --":
                photo_url = candidate_photos.get(selected_candidate)
                if photo_url:
                    st.image(f"{st.session_state.api_url}{photo_url}", width=100, caption=selected_candidate)

            selections[pos_id] = selected_candidate
        
        st.divider()
        submitted = st.form_submit_button("Confirm and Submit My Final Vote", use_container_width=True, type="primary")
        
        if submitted:
            all_selections_valid = True
            for pos_id, candidate_name in selections.items():
                if candidate_name == "-- Select a Candidate --":
                    pos_title = next((p["title"] for p in positions if p["id"] == pos_id), "a position")
                    st.warning(f"You must select a candidate for {pos_title}.")
                    all_selections_valid = False
            
            if all_selections_valid:
                with st.spinner("Submitting your vote..."):
                    
                    # --- THIS IS THE FIXED LOGIC ---
                    response_data = submit_vote(selections, student_identifier)
                    
                    # If the API call is successful, it will return a dictionary.
                    # If it fails, it will return None.
                    if response_data:
                        st.balloons()
                        # We can even show the success message from the backend.
                        success_message = response_data.get("message", "Your vote has been recorded!")
                        st.success(success_message)
                        st.info("This screen will reset for the next student in 5 seconds.")
                        time.sleep(5)
                        st.session_state.page = "login"
                        st.rerun()
                    # No 'else' is needed, because if the API fails, handle_request in api.py
                    # will automatically show an error toast.