import streamlit as st
from src.pages.home import show_home
from src.pages.search import show_search
from src.pages.admin import show_admin
from src.utils.auth import check_authentication

def main():
    st.set_page_config(
        page_title="Support Tool System",
        page_icon="🔍",
        layout="wide"
    )

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Authentication check
    if not st.session_state.authenticated:
        check_authentication()
        return

    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Search", "Admin"])

    # Page routing
    if page == "Home":
        show_home()
    elif page == "Search":
        show_search()
    elif page == "Admin":
        show_admin()

if __name__ == "__main__":
    main()
