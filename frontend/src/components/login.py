import streamlit as st
from src.utils.auth import init_auth, save_auth, clear_auth, get_auth_status
import logging

def show_login():
    """Display login form and handle authentication"""
    # Initialize auth state
    init_auth()
    
    # Get current auth status
    auth_status = get_auth_status()
        
    if auth_status["is_authenticated"]:
        user = auth_status["user"]
        st.write(f"Logged in as:")
        st.markdown(f"[{user.get('email')}](mailto:{user.get('email')})")
        
        # Show user role
        if user.get("is_admin"):
            st.caption("Admin User")
        elif user.get("is_superuser"):
            st.caption("Super User")
        else:
            st.caption("Regular User")
            
        if st.button("Logout", key="logout_button", use_container_width=True):
            clear_auth()
            st.rerun()
    else:
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password")
                    return
                    
                try:
                    # Attempt login
                    response = st.session_state.api_client.login(email, password)
                    if response and "access_token" in response:
                        # Save auth state
                        save_auth(response["access_token"], response["user"])
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                except Exception as e:
                    logging.error(f"Login error: {str(e)}")
                    st.error("Login failed. Please try again.")
