import streamlit as st
import pandas as pd

def show_admin():
    st.title("Admin Dashboard")
    
    # Check if user has admin privileges
    if not st.session_state.get("is_admin", False):
        st.error("You do not have permission to access this page")
        return
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["Data Upload", "System Stats", "User Management"])
    
    with tab1:
        show_data_upload()
    
    with tab2:
        show_system_stats()
    
    with tab3:
        show_user_management()

def show_data_upload():
    st.header("Data Upload")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            # Preview the data
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            if st.button("Process Data"):
                # Upload to backend
                if st.session_state.api_client.upload_data(uploaded_file):
                    st.success("Data uploaded and processed successfully!")
                else:
                    st.error("Failed to upload data")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def show_system_stats():
    st.header("System Statistics")
    
    # Placeholder for system stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tickets", "1,234")
    
    with col2:
        st.metric("Active Users", "50")
    
    with col3:
        st.metric("Response Time", "1.2s")

def show_user_management():
    st.header("User Management")
    
    # Placeholder for user management interface
    st.info("User management interface coming soon...")
