import streamlit as st
import pandas as pd
from datetime import datetime
from src.services.markdown_converter import MarkdownConverter
from src.services.embedding import EmbeddingService

def show_admin():
    st.title("Admin Dashboard")
    
    # Check if user is logged in
    if not st.session_state.get("access_token"):
        st.error("Please log in first")
        return
    
    # Check if user has admin privileges
    user_data = st.session_state.get("user", {})
    if not user_data.get("is_admin", False):
        st.error("You do not have permission to access this page")
        return
    
    # Initialize services if not exists
    if "markdown_service" not in st.session_state:
        st.session_state.markdown_service = MarkdownConverter()
        st.session_state.embedding_service = EmbeddingService()
    
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
    
    # File upload section
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            # Preview the data
            df = pd.read_csv(uploaded_file)
            
            # Basic validation
            required_columns = [
                'Issue Type', 'Priority', 'Issue key', 'Summary', 
                'Status', 'Created', 'Updated'
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                return
            
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            # Display file statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            
            # Process button with progress bar
            if st.button("Process Data"):
                with st.spinner("Processing data..."):
                    try:
                        # Reset the file pointer
                        uploaded_file.seek(0)
                        
                        # Upload to backend
                        response = st.session_state.api_client.upload_data(uploaded_file)
                        
                        if response and response.get("total_processed"):
                            st.success(f"""
                                Data processed successfully!
                                - Total records processed: {response['total_processed']}
                                - Markdown files generated: {response.get('markdown_files_generated', 0)}
                            """)
                        else:
                            st.error("Failed to process data")
                            
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
                        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

def show_system_stats():
    st.header("System Statistics")
    
    try:
        # Get stats from backend
        stats = st.session_state.api_client.get_system_stats()
        
        if stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Documents", stats.get("total_documents", 0))
            
            with col2:
                last_updated = stats.get("last_updated")
                if last_updated:
                    try:
                        last_updated = datetime.fromisoformat(last_updated)
                        last_updated = last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                st.metric("Last Updated", last_updated or "Never")
            
            # Add refresh button
            if st.button("Refresh Stats"):
                st.experimental_rerun()
                
        else:
            st.warning("No statistics available")
            
    except Exception as e:
        st.error(f"Error fetching system stats: {str(e)}")

def show_user_management():
    st.header("User Management")
    st.info("User management interface coming soon...")
    
    # Display current user info
    user_data = st.session_state.get("user", {})
    if user_data:
        st.write("Current User:")
        st.json({
            "Email": user_data.get("email"),
            "Full Name": user_data.get("full_name"),
            "Is Admin": user_data.get("is_admin", False),
            "Is Active": user_data.get("is_active", False)
        })
