# ui/admin_tabs/_1_results_stats_tab.py (Fully Updated and Corrected)

import streamlit as st
import pandas as pd
from ui.api import get_results, export_results_as_csv

def render(password: str):
    """
    Renders the Live Results & Stats tab for the admin dashboard.
    This version is corrected to avoid caching errors and uses the new API structure.
    """
    st.subheader("Live Election Dashboard")
    
    # Simple refresh button, no complex caching needed on the main button
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

    # Fetch data directly
    results_response = get_results(password)

    if results_response: # API call was successful
        data = results_response
        
        # --- Live Voter Turnout ---
        st.markdown("#### Voter Turnout")
        turnout_data = data.get("voter_turnout", {})
        total_students = turnout_data.get("total_students", 0)
        votes_cast = turnout_data.get("total_votes_cast", 0)
        
        if total_students > 0:
            turnout_percentage = (votes_cast / total_students)
            st.progress(turnout_percentage, text=f"{turnout_percentage:.1%} Voted")
        else:
            turnout_percentage = 0
            st.progress(0, text="No students registered")
            
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        stat_col1.metric("Total Registered Students", f"{total_students} 🧑‍🎓")
        stat_col2.metric("Total Votes Cast", f"{votes_cast} 🗳️")
        stat_col3.metric("Turnout", f"{turnout_percentage:.1%}")
        
        st.divider()

        # --- Dynamic Results Display ---
        st.markdown("#### Live Results")
        results_data = data.get("results", {})
        
        if not results_data:
            st.info("No positions have been configured for the election yet.")
        else:
            for pos_id, pos_data in results_data.items():
                with st.container(border=True):
                    st.subheader(pos_data.get("position_title", "Unnamed Position"))
                    st.metric("Winner(s)", pos_data.get("winner", "N/A"))
                    
                    vote_counts = pos_data.get("vote_counts", {})
                    if vote_counts:
                        df = pd.DataFrame.from_dict(vote_counts, orient='index', columns=['Votes'])
                        st.bar_chart(df)
                    else:
                        st.write("No votes cast for this position yet.")
        
        st.divider()

        # --- Export Results ---
        st.markdown("#### Export Results")
        st.write("Download the complete election results as a CSV file for official records.")
        
        if st.button("📥 Export Results to CSV"):
            with st.spinner("Generating CSV file..."):
                export_response = export_results_as_csv(password)
                if export_response and export_response.status_code == 200:
                    st.download_button(
                        label="Click here to Download CSV",
                        data=export_response.content,
                        file_name="election_results.csv",
                        mime="text/csv",
                    )
                else:
                    st.toast("❌ Failed to generate the export file.", icon="🔥")
    else:
        # This message shows if the API connection itself failed
        st.warning("Could not fetch results from the server. Refresh the dashboard or check the backend.")