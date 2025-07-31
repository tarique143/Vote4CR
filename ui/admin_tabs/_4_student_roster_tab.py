# ui/admin_tabs/_4_student_roster_tab.py (Fully Updated and Corrected)

import streamlit as st
import pandas as pd
# FIXED: Removed the unnecessary import of get_stream_config
from ui.api import get_all_students, bulk_upload_students
from typing import Dict, Any

def render(settings: Dict[str, Any], password: str):
    """
    Renders the Student Roster Management tab.
    This version is corrected to use the passed-in settings object
    instead of making a separate API call.
    """
    st.subheader("Manage Student Roster")

    # --- Bulk Student Upload ---
    with st.expander("📂 Bulk Upload Students from File", expanded=False):
        st.info(
            "Upload a CSV or Excel file with the columns: `name`, `roll_number`, `stream`, `division`. "
            "The division must match one of the configured divisions for that stream. Leave it empty for streams with no divisions."
        )
        
        @st.cache_data
        def create_template():
            template_data = {
                'name': ['Suresh Kumar', 'Anita Sharma', 'Rajesh Gupta'],
                'roll_number': [101, 102, 201],
                'stream': ['Science', 'Science', 'Arts'],
                'division': ['A', 'B', '']
            }
            df = pd.DataFrame(template_data)
            return df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Template CSV",
            data=create_template(),
            file_name="student_template.csv",
            mime="text/csv",
        )

        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"]
        )
        
        if uploaded_file is not None:
            if st.button("Upload and Process File"):
                with st.spinner("Processing file... This may take a moment."):
                    response = bulk_upload_students(uploaded_file, password)
                    if response:
                        data = response
                        st.toast(f"✅ File processed! Added: {data['students_added']}, Duplicates skipped: {data['duplicates_found']}.")
                        if data['errors']:
                            st.warning("Some rows had errors:")
                            st.json(data['errors'])
                        st.rerun()
    
    st.divider()

    # --- Display Roster and Manual Add ---
    
    # Get the academic structure from the passed-in settings object
    academic_structure = settings.get("academic_structure", [])
    if not academic_structure:
        st.warning("No academic streams have been configured. Please add them in the 'Election Settings' tab.")
        return

    # --- Display Roster ---
    st.markdown("#### Full Student Roster")
    search_term = st.text_input("Search Students by Name or Roll No:", placeholder="Type to filter...")
    
    with st.spinner("Loading student list..."):
        students_list = get_all_students(password)
        if students_list:
            df = pd.DataFrame(students_list)
            
            if search_term:
                df = df[
                    df["name"].str.contains(search_term, case=False, na=False) |
                    df["roll_number"].astype(str).str.contains(search_term, na=False)
                ]
            
            st.dataframe(df, use_container_width=True, height=500)
        else:
            st.info("No students have been added to the roster yet. Use the Bulk Upload feature above to add them.")