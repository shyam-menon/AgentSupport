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

    # Initialize API client if not exists
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()

    # Initialize auth state from URL params
    init_auth()
    auth_status = get_auth_status()

    # Show login component in sidebar
    with st.sidebar:
        show_login()

    # Navigation - only show if logged in
    if auth_status["is_authenticated"]:
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
    else:
        st.title("Welcome to Support Tool System")
        st.info("Please log in to continue")

if __name__ == "__main__":
    main()
