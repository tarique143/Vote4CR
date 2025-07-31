# ui/admin_tabs/_2_election_settings_tab.py (Fully Updated and Corrected)

import streamlit as st
from ui.api import update_election_settings, reset_election, clear_candidate_list, clear_student_roster
from typing import Dict, Any

def render(settings: Dict[str, Any], password: str):
    """
    Renders the Election Settings tab.
    This final version includes an ultra-safe Danger Zone with text confirmation for all destructive actions
    and uses the new standardized API calls.
    """
    st.subheader("Manage Global Election Settings")
    st.info("Changes made here will affect the entire application, including the student voting kiosk.")

    # Create a deep copy to modify, so we can detect changes
    new_settings = settings.copy()

    # --- College Branding ---
    st.markdown("#### College Branding")
    new_settings["college_info"]["college_name"] = st.text_input(
        "College Name", 
        value=settings.get("college_info", {}).get("college_name", "Demo College")
    )
    new_settings["college_info"]["college_logo_url"] = st.text_input(
        "College Logo URL (Optional)",
        value=settings.get("college_info", {}).get("college_logo_url", "")
    )
    st.divider()

    # --- Voting Session & Identification ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Voting Session Control")
        current_status = settings.get("voting_status", "CLOSED")
        new_settings["voting_status"] = st.selectbox(
            "Voting Status",
            ["OPEN", "CLOSED"],
            index=0 if current_status == "OPEN" else 1
        )
    with col2:
        st.markdown("#### Student Identification Method")
        current_id_mode = settings.get("identification_mode", "name_and_id")
        new_settings["identification_mode"] = st.selectbox(
            "Identification Mode",
            ["name_and_id", "id_only"],
            index=0 if current_id_mode == "name_and_id" else 1,
            format_func=lambda x: "Name & Roll No" if x == "name_and_id" else "Roll No Only"
        )
    st.divider()

    # --- Dynamic Position Management ---
    st.markdown("#### Manage Election Positions")
    positions = new_settings.get("positions", [])
    for i, pos in enumerate(positions):
        with st.container(border=True):
            col_pos_1, col_pos_2, col_pos_3, col_pos_4 = st.columns([3, 3, 2, 1])
            pos["title"] = col_pos_1.text_input(f"Position Title", value=pos["title"], key=f"pos_title_{i}")
            pos["id"] = col_pos_2.text_input(f"Unique ID", value=pos["id"], key=f"pos_id_{i}", help="A unique ID, e.g., 'president'. No spaces.")
            pos["gender_requirement"] = col_pos_3.selectbox(
                f"Gender Rule", [None, "boy", "girl"],
                index=[None, "boy", "girl"].index(pos.get("gender_requirement")),
                format_func=lambda x: "Any" if x is None else x.capitalize(),
                key=f"pos_gender_{i}"
            )
            if col_pos_4.button("❌", key=f"del_pos_{i}", help="Remove this position"):
                positions.pop(i)
                st.rerun()
    if st.button("Add New Position"):
        positions.append({"id": f"new_pos_{len(positions)}", "title": "New Position", "gender_requirement": None})
        st.rerun()
    new_settings["positions"] = positions
    st.divider()

    # --- Dynamic Academic Structure Management ---
    st.markdown("#### Manage Academic Structure")
    academic_structure = new_settings.get("academic_structure", [])
    for i, stream in enumerate(academic_structure):
        with st.container(border=True):
            col_stream_1, col_stream_2, col_stream_3 = st.columns([3, 5, 1])
            stream["stream_name"] = col_stream_1.text_input("Stream Name", value=stream["stream_name"], key=f"stream_name_{i}")
            divisions_str = ",".join(stream["divisions"])
            new_divisions_str = col_stream_2.text_input("Divisions (comma-separated)", value=divisions_str, key=f"stream_divs_{i}")
            stream["divisions"] = sorted([d.strip().upper() for d in new_divisions_str.split(',') if d.strip()])
            if col_stream_3.button("❌", key=f"del_stream_{i}", help="Remove this stream"):
                academic_structure.pop(i)
                st.rerun()
    if st.button("Add New Stream"):
        academic_structure.append({"stream_name": "New Stream", "divisions": []})
        st.rerun()
    new_settings["academic_structure"] = academic_structure
    st.divider()

    # --- Save All Settings Button ---
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        with st.spinner("Saving settings..."):
            response = update_election_settings(new_settings, password)
            if response:
                st.toast("✅ Settings saved successfully!", icon="🎉")
                st.rerun()

    st.divider()
    
    # --- Ultra-Safe Danger Zone ---
    with st.expander("⚠️ Danger Zone: Database Management", expanded=False):
        st.error("These actions are permanent and cannot be undone. Proceed with extreme caution.")

        # Action 1: Reset Election
        st.markdown("---")
        st.write("**Reset Election** (Clears all votes, but keeps students and candidates)")
        reset_confirm = st.text_input("To confirm, type `RESET ELECTION` into the box below:", key="reset_confirm_text")
        if st.button("Permanently Reset Election", disabled=(reset_confirm != "RESET ELECTION")):
            with st.spinner("Resetting election..."):
                if reset_election(password):
                    st.toast("✅ Success! All votes have been cleared.")
                    st.rerun()

        # Action 2: Clear Candidate List
        st.markdown("---")
        st.write("**Clear Candidate List** (Deletes ALL candidates)")
        candidate_confirm = st.text_input("To confirm, type `DELETE CANDIDATES` into the box below:", key="candidate_confirm_text")
        if st.button("Permanently Delete All Candidates", disabled=(candidate_confirm != "DELETE CANDIDATES")):
            with st.spinner("Deleting all candidates..."):
                if clear_candidate_list(password):
                    st.toast("✅ Success! All candidates deleted.")
                    st.rerun()

        # Action 3: Clear Student Roster
        st.markdown("---")
        st.write("**Clear Student Roster** (Deletes ALL registered students)")
        student_confirm = st.text_input("To confirm, type `DELETE STUDENTS` into the box below:", key="student_confirm_text")
        if st.button("Permanently Delete Student Roster", disabled=(student_confirm != "DELETE STUDENTS")):
            with st.spinner("Deleting all students..."):
                if clear_student_roster(password):
                    st.toast("✅ Success! All students deleted.")
                    st.rerun()