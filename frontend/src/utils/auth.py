import streamlit as st
from .api_client import APIClient

def check_authentication():
    """Handle user authentication"""
    st.title("Login")
    
    api_client = APIClient()
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username and password:
            if api_client.login(username, password):
                st.session_state.authenticated = True
                st.session_state.api_client = api_client
                st.rerun()  # Updated from experimental_rerun
            else:
                st.error("Invalid username or password")
        else:
            st.error("Please enter both username and password")
