import streamlit as st
import pandas as pd
from datetime import datetime
from src.services.markdown_converter import MarkdownConverter
from src.services.embedding import EmbeddingService
import tempfile
import os

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
            
            # Map the columns to expected format
            column_mapping = {
                'Issue Type': 'issue_type',
                'Priority': 'priority',
                'Issue key': 'id',
                'Summary': 'title',
                'Status': 'status',
                'Assignee': 'assignee',
                'Reporter': 'reporter',
                'Created': 'created_at',
                'Updated': 'updated_at',
                'Custom field (Bug Resolution)': 'resolution',
                'Custom field (Section/Asset Team)': 'affected_system',
                'Summary': 'description',  # Using Summary as description for now
            }
            
            # Check if required source columns exist
            source_columns = list(column_mapping.keys())
            missing_columns = [col for col in source_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                st.info("The CSV file must contain the following columns: " + ", ".join(source_columns))
                return
            
            # Rename columns to match expected format
            df_processed = df.rename(columns=column_mapping)
            
            # Save processed DataFrame to a temporary CSV
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='', encoding='utf-8') as temp_file:
                df_processed.to_csv(temp_file.name, index=False)
                temp_file_path = temp_file.name
            
            st.write("Preview of processed data:")
            st.dataframe(df_processed.head())
            
            # Display file statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Records", len(df_processed))
            with col2:
                st.metric("Columns", len(df_processed.columns))
            
            # Process button with progress bar
            if st.button("Process Data"):
                with st.spinner("Processing data..."):
                    try:
                        # Check if user is logged in and has admin privileges
                        if not st.session_state.get("access_token"):
                            st.error("Please log in first")
                            return
                        
                        user_data = st.session_state.get("user", {})
                        if not user_data.get("is_admin", False):
                            st.error("You do not have permission to access this page")
                            return
                            
                        # Create a file object from the temp file
                        with open(temp_file_path, 'rb') as processed_file:
                            # Upload to backend
                            response = st.session_state.api_client.upload_data(processed_file)
                            
                            if response and response.get("total_processed"):
                                st.success(f"""
                                    Data processed successfully!
                                    - Total records processed: {response['total_processed']}
                                    - Markdown files generated: {response.get('markdown_files_generated', 0)}
                                """)
                            else:
                                st.error("Failed to process data. Please check your permissions and try again.")
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
                    finally:
                        # Clean up temporary file
                        try:
                            os.remove(temp_file_path)
                        except:
                            pass
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
