import streamlit as st
from src.services.admin import AdminService
import logging

def show_system_stats():
    """Show system statistics"""
    try:
        admin_service = AdminService()
        if "api_client" in st.session_state:
            admin_service.api_client = st.session_state.api_client
            
        stats = admin_service.get_stats()
        
        st.subheader("System Statistics")
        
        # Document Stats
        st.markdown("#### Document Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents", stats.get("total_documents", 0))
            
        with col2:
            st.metric("Markdown Files", stats.get("markdown_files", 0))
            
        with col3:
            st.metric("Embeddings", stats.get("embedding_count", 0))
            
        # Last Updated Stats
        st.markdown("#### Update Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Last Updated", stats.get("last_updated", "Never"))
            
        with col2:
            st.metric("Vector Store Status", "✅ Connected" if stats.get("vector_store_healthy", False) else "❌ Error")
        
        # Storage Stats
        if stats.get("storage_info"):
            st.markdown("#### Storage Information")
            storage = stats["storage_info"]
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Markdown Directory Size", f"{storage.get('markdown_size_mb', 0):.2f} MB")
            
            with col2:
                st.metric("Vector Store Size", f"{storage.get('vector_store_size_mb', 0):.2f} MB")
        
        # Sample Records
        if stats.get("sample_records"):
            st.markdown("#### Sample Records")
            with st.expander("View Sample Data"):
                for record in stats["sample_records"][:3]:
                    st.code(str(record), language="json")
        
        # Refresh Button
        if st.button("Refresh Stats", type="primary", key="refresh_stats"):
            st.rerun()
            
    except Exception as e:
        st.error(f"Error fetching system stats: {str(e)}")

def show_data_upload():
    """Show data upload section"""
    try:
        st.subheader("Upload CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
        
        if uploaded_file is not None:
            if st.button("Process File", key="process_file", type="primary"):
                admin_service = AdminService()
                if "api_client" in st.session_state:
                    admin_service.api_client = st.session_state.api_client
                    
                with st.spinner("Processing CSV file..."):
                    result = admin_service.process_csv_file(uploaded_file)
                    if result.get("success"):
                        st.success(f"CSV file processed successfully! {result.get('message', '')}")
                        st.rerun()
                    else:
                        st.error(f"Error processing file: {result.get('error')}")
                        
    except Exception as e:
        st.error(f"Error in data upload: {str(e)}")

def show_user_management():
    """Show user management section"""
    st.subheader("User Management")
    st.info("User management features coming soon!")

def show_admin():
    """Show admin dashboard"""
    user = st.session_state.get("user", {})
    if not user.get("is_admin"):
        st.error("You must be an admin to access this page")
        return

    st.title("Admin Dashboard")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Data Management", "System Stats", "User Management"])
    
    with tab1:
        # Data Management section
        st.header("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV Upload
            st.subheader("Upload CSV")
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                if st.button("Process CSV", type="primary"):
                    with st.spinner("Processing CSV file..."):
                        try:
                            admin_service = AdminService()
                            result = admin_service.process_csv_file(uploaded_file)
                            if result.get("success"):
                                st.success(f"Successfully processed {result.get('processed_records', 0)} records")
                                st.rerun()
                            else:
                                st.error(f"Error processing CSV: {result.get('error')}")
                        except Exception as e:
                            st.error(f"Error processing file: {str(e)}")
        
        with col2:
            # Clear Embeddings
            st.subheader("Clear Data")
            if st.button("Clear All Embeddings", type="secondary"):
                if st.warning("This will delete all embeddings. Are you sure?"):
                    try:
                        admin_service = AdminService()
                        response = admin_service.clear_embeddings()
                        if response.get("success"):
                            st.success("Successfully cleared all embeddings")
                            st.rerun()
                        else:
                            st.error(f"Failed to clear embeddings: {response.get('error')}")
                    except Exception as e:
                        st.error(f"Error clearing embeddings: {str(e)}")
        
    with tab2:
        show_system_stats()
        
    with tab3:
        show_user_management()
