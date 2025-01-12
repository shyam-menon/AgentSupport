import streamlit as st
from src.pages.home import show_home
from src.pages.search import show_search
from src.pages.admin import show_admin
from src.components.login import show_login
from src.utils.api_client import APIClient
from src.utils.auth import init_auth, get_auth_status
import logging

def main():
    st.set_page_config(
        page_title="Support Tool System",
        page_icon="🔍",
        layout="wide"
    )

    logging.info("Starting main app")
    logging.info(f"Current session state keys: {[k for k in st.session_state.keys()]}")

    # Initialize API client if not exists
    if "api_client" not in st.session_state:
        logging.info("Initializing new API client")
        st.session_state.api_client = APIClient()
    else:
        logging.info("Using existing API client")

    # Initialize auth state from URL params
    logging.info("Initializing auth state")
    init_auth()
    auth_status = get_auth_status()
    logging.info(f"Auth status: {auth_status}")

    # Show login component in sidebar
    with st.sidebar:
        show_login()
        
    # Only show content if authenticated
    if not auth_status["is_authenticated"]:
        st.warning("Please log in to access the application")
        return

    # Navigation - only show if logged in
    st.sidebar.title("Navigation")
    options = ["Home", "Search"]
    
    # Add Admin option if user has admin privileges
    if auth_status["user"].get("is_admin", False):
        options.append("Admin")
            
    page = st.sidebar.radio("Go to", options)

    # Page routing
    if page == "Home":
        show_home()
    elif page == "Search":
        show_search()
    elif page == "Admin":
        show_admin()

if __name__ == "__main__":
    main()
