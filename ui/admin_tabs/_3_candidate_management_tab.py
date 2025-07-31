# ui/admin_tabs/_3_candidate_management_tab.py (Fully Updated and Corrected)

import streamlit as st
from ui.api import get_candidates, add_candidate, upload_candidate_photo, delete_candidate
from typing import Dict, Any

def render(settings: Dict[str, Any], password: str):
    """
    Renders the Candidate Management tab.
    This version uses the new standardized API calls and fixes the tab switching bug.
    """
    st.subheader("Manage Election Candidates")

    # Fetch all current candidates
    all_candidates = get_candidates()
    
    # Get the list of available positions from the settings
    positions = settings.get("positions", [])
    if not positions:
        st.warning("No election positions have been configured. Please add positions in the 'Election Settings' tab first.")
        return

    col1, col2 = st.columns([0.4, 0.6])

    # --- Column 1: Add New Candidate Form ---
    with col1:
        st.markdown("#### Add New Candidate")
        with st.form("add_candidate_form"):
            
            position_options = {pos["title"]: pos["id"] for pos in positions}
            
            selected_title = st.selectbox(
                "Select Position",
                options=list(position_options.keys())
            )
            
            candidate_name = st.text_input("Candidate's Full Name")
            gender = st.selectbox("Gender", ["boy", "girl"])
            photo_file = st.file_uploader(
                "Upload Candidate Photo (Optional)",
                type=["png", "jpg", "jpeg"]
            )
            
            submitted = st.form_submit_button("Add Candidate to Roster")

            if submitted:
                if not candidate_name or not selected_title:
                    st.warning("Please provide the candidate's name and select a position.")
                else:
                    position_id = position_options[selected_title]
                    candidate_data = {"name": candidate_name, "position_id": position_id, "gender": gender}
                    
                    with st.spinner(f"Adding {candidate_name}..."):
                        # Step 1: Add the candidate's text data
                        add_response = add_candidate(candidate_data, password)
                        
                        if add_response:
                            st.toast(f"✅ Candidate '{candidate_name}' added!", icon="🎉")
                            
                            # Step 2: If a photo was provided, upload it
                            if photo_file is not None:
                                st.toast("Uploading photo...", icon="📤")
                                upload_candidate_photo(candidate_name, position_id, photo_file, password)
                            st.rerun()

    # --- Column 2: Display Current Candidates ---
    with col2:
        st.markdown("#### Current Candidates Roster")
        
        if not all_candidates:
            st.info("No candidates have been added yet.")
        else:
            # Group candidates by position for better display
            for pos in positions:
                st.markdown(f"##### Candidates for {pos['title']}")
                
                candidates_for_pos = [c for c in all_candidates if c.get("position_id") == pos["id"]]
                
                if not candidates_for_pos:
                    st.write("_No candidates added for this position yet._")
                else:
                    for cand in candidates_for_pos:
                        with st.container(border=True):
                            c_col1, c_col2, c_col3 = st.columns([0.2, 0.6, 0.2])
                            
                            with c_col1:
                                if cand.get("photo_url"):
                                    st.image(f"{st.session_state.api_url}{cand['photo_url']}", width=60)
                                else:
                                    st.image("assets/default_logo.png", width=60)
                            
                            with c_col2:
                                st.write(f"**{cand['name']}**")
                                st.caption(f"Gender: {cand['gender'].capitalize()}")
                            
                            with c_col3:
                                if st.button("🗑️ Delete", key=f"del_{pos['id']}_{cand['name']}", use_container_width=True):
                                    with st.spinner("Deleting..."):
                                        candidate_data_to_delete = {"name": cand['name'], "position_id": pos['id'], "gender": cand['gender']}
                                        delete_candidate(candidate_data_to_delete, password)
                                        st.toast(f"🗑️ Candidate '{cand['name']}' deleted.")
                                        st.rerun()