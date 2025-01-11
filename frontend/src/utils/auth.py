import streamlit as st
from typing import Optional, Dict
import json
import logging
from datetime import datetime, timedelta

def init_auth():
    """Initialize authentication state from URL params"""
    try:
        # Try to get auth data from URL params
        auth_data = st.query_params.get("auth")
        if auth_data:
            auth_data = json.loads(auth_data)
            st.session_state.access_token = auth_data.get("access_token")
            st.session_state.user = auth_data.get("user")
            
            # Update API client token
            if "api_client" in st.session_state:
                st.session_state.api_client.token = st.session_state.access_token
                
    except Exception as e:
        logging.error(f"Error initializing auth: {e}")
        
    # Ensure session state is initialized
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user" not in st.session_state:
        st.session_state.user = None

def save_auth(token: str, user: Dict):
    """Save authentication state to URL params"""
    try:
        # Save to session state
        st.session_state.access_token = token
        st.session_state.user = user
        
        # Update API client token
        if "api_client" in st.session_state:
            st.session_state.api_client.token = token
        
        # Save to URL params
        auth_data = {
            "access_token": token,
            "user": user
        }
        st.query_params["auth"] = json.dumps(auth_data)
            
    except Exception as e:
        logging.error(f"Error saving auth: {e}")

def clear_auth():
    """Clear authentication state"""
    try:
        # Clear session state
        st.session_state.access_token = None
        st.session_state.user = None
        
        # Clear API client token
        if "api_client" in st.session_state:
            st.session_state.api_client.token = None
        
        # Clear URL params
        st.query_params.clear()
            
    except Exception as e:
        logging.error(f"Error clearing auth: {e}")

def get_auth_status() -> Dict:
    """Get current authentication status"""
    return {
        "is_authenticated": bool(st.session_state.get("access_token")),
        "user": st.session_state.get("user")
    }
