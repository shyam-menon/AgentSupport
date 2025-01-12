import streamlit as st
from typing import Optional, Dict
import json
import logging
from datetime import datetime, timedelta

def init_auth():
    """Initialize authentication state from URL params"""
    logging.info("Initializing auth state")
    try:
        # Try to get auth data from URL params
        auth_data = st.query_params.get("auth")
        logging.info(f"Auth data from URL: {auth_data is not None}")
        
        if auth_data:
            auth_data = json.loads(auth_data)
            st.session_state.access_token = auth_data.get("access_token")
            st.session_state.user = auth_data.get("user")
            logging.info("Auth data loaded from URL params")
            
            # Update API client token
            if "api_client" in st.session_state:
                st.session_state.api_client.token = st.session_state.access_token
                logging.info("Updated API client token")
                
    except Exception as e:
        logging.error(f"Error initializing auth: {e}")
        
    # Ensure session state is initialized
    if "access_token" not in st.session_state:
        logging.info("Initializing access_token in session state")
        st.session_state.access_token = None
    if "user" not in st.session_state:
        logging.info("Initializing user in session state")
        st.session_state.user = None

def save_auth(token: str, user: Dict):
    """Save authentication state to URL params"""
    logging.info("Saving auth state")
    try:
        # Save to session state
        st.session_state.access_token = token
        st.session_state.user = user
        logging.info("Saved auth data to session state")
        
        # Update API client token
        if "api_client" in st.session_state:
            st.session_state.api_client.token = token
            logging.info("Updated API client token")
        
        # Save to URL params
        auth_data = {
            "access_token": token,
            "user": user
        }
        st.query_params["auth"] = json.dumps(auth_data)
        logging.info("Saved auth data to URL params")
        
    except Exception as e:
        logging.error(f"Error saving auth: {e}")

def clear_auth():
    """Clear authentication state"""
    logging.info("Clearing auth state")
    try:
        # Log current state
        logging.info(f"Current session state keys: {[k for k in st.session_state.keys()]}")
        
        # Clear session state
        st.session_state.access_token = None
        st.session_state.user = None
        logging.info("Cleared access_token and user from session state")
        
        # Clear API client token
        if "api_client" in st.session_state:
            st.session_state.api_client.token = None
            logging.info("Cleared API client token")
        
        # Clear URL params
        st.query_params.clear()
        logging.info("Cleared URL params")
            
    except Exception as e:
        logging.error(f"Error clearing auth: {e}")

def get_auth_status() -> Dict:
    """Get current authentication status"""
    logging.info("Checking auth status")
    token = st.session_state.get("access_token")
    user = st.session_state.get("user")
    
    logging.info(f"Token present: {token is not None}")
    logging.info(f"User present: {user is not None}")
    
    return {
        "is_authenticated": bool(token and user),
        "user": user
    }
