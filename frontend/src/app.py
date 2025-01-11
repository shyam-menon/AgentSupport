import streamlit as st
from src.pages.home import show_home
from src.pages.search import show_search
from src.pages.admin import show_admin
from src.components.login import show_login
from src.utils.api_client import APIClient

def main():
    st.set_page_config(
        page_title="Support Tool System",
        page_icon="🔍",
        layout="wide"
    )

    # Initialize API client if not exists
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()

    # Show login component in sidebar
    with st.sidebar:
        show_login()

    # Navigation - only show if logged in
    if st.session_state.get("access_token"):
        st.sidebar.title("Navigation")
        options = ["Home", "Search"]
        
        # Add Admin option if user has admin privileges
        if st.session_state.get("user", {}).get("is_admin", False):
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
