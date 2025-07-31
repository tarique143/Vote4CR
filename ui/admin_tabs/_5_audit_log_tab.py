# ui/admin_tabs/_5_audit_log_tab.py (New File)

import streamlit as st
import pandas as pd
from ui.api import get_audit_logs

def render(password: str):
    """
    Renders the Audit Log tab, displaying all logged activities.
    """
    st.subheader("System Activity Log")
    st.info("This log shows the last 200 important actions taken by administrators and the system.")

    if st.button("🔄 Refresh Logs"):
        # We don't need to do anything here, Streamlit's rerun will re-fetch the data.
        pass

    # Fetch the logs from the backend
    with st.spinner("Loading activity logs..."):
        logs_data = get_audit_logs(password)

        if logs_data is not None:
            if not logs_data:
                st.info("No activity has been logged yet.")
            else:
                # Convert the list of log dictionaries to a Pandas DataFrame for better display
                df = pd.DataFrame(logs_data)
                
                # Convert timestamp string to a more readable format.
                # This assumes the backend sends UTC timestamps.
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Rename columns for a cleaner look
                df.rename(columns={
                    'timestamp': 'Timestamp (UTC)',
                    'actor': 'Actor',
                    'action': 'Action',
                    'details': 'Details'
                }, inplace=True)

                # Display the DataFrame as a table
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_order=("Timestamp (UTC)", "Actor", "Action", "Details")
                )
        else:
            # This message shows if the API call itself failed
            st.error("Failed to load audit logs from the server.")