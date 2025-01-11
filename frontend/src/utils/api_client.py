import requests
from typing import Dict, List
import os
from dotenv import load_dotenv
import logging
import streamlit as st

load_dotenv()

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8080")
        # Initialize token from session state if available
        self.token = st.session_state.get("access_token")

    def _get_headers(self):
        """Get headers with authentication token if available"""
        headers = {}
        # Always get latest token from session state
        self.token = st.session_state.get("access_token")
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get_form_headers(self):
        """Get headers for form data with authentication token if available"""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # Always get latest token from session state
        self.token = st.session_state.get("access_token")
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get_multipart_headers(self):
        """Get headers for multipart form data (file uploads) with authentication token if available"""
        headers = {}  # Don't set Content-Type, let requests set it with boundary
        # Always get latest token from session state
        self.token = st.session_state.get("access_token")
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user and store token
        Returns the response data if successful, None if failed
        """
        try:
            logging.info(f"Attempting login for user: {username}")
            # Use form data instead of JSON for OAuth2 password flow
            data = {
                "username": username,
                "password": password,
                "grant_type": "password"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/token",
                data=data,
                headers=self._get_form_headers()  # Use form headers for login
            )
            
            if response.status_code == 401:
                logging.error(f"Authentication failed for user {username} - invalid credentials")
                return None
                
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            logging.info(f"Login successful for user: {username}")
            logging.debug(f"Token received: {self.token[:10]}...")  # Log first 10 chars of token
            return data
        except Exception as e:
            logging.error(f"Login failed for user {username}: {str(e)}")
            return None

    def search_tickets(self, query: Dict) -> List[Dict]:
        """Search for similar tickets"""
        try:
            response = requests.post(
                f"{self.base_url}/search",
                json=query,
                headers=self._get_headers()
            )
            if response.status_code == 401:
                logging.error("Unauthorized - token may have expired")
                return []
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to search tickets: {str(e)}")
            raise Exception(f"Failed to search tickets: {str(e)}")

    def upload_data(self, file) -> Dict:
        """
        Upload CSV data file
        Returns: Dict containing processing results
        """
        try:
            if not self.token:
                logging.error("Upload failed: No authentication token")
                return None
                
            logging.info(f"Uploading file: {getattr(file, 'name', 'unknown')}")
            logging.debug(f"Using token: {self.token[:10]}...")  # Log first 10 chars of token
            
            files = {"file": file}
            headers = self._get_multipart_headers()
            logging.debug(f"Request headers: {headers}")
            
            response = requests.post(
                f"{self.base_url}/admin/upload",
                files=files,
                headers=headers
            )
            
            logging.info(f"Upload response status: {response.status_code}")
            if response.status_code != 200:
                logging.error(f"Upload failed with status {response.status_code}")
                logging.error(f"Response content: {response.text}")
            
            if response.status_code == 401:
                logging.error("Unauthorized - token may have expired")
                return None
            elif response.status_code == 403:
                logging.error("Forbidden - user may not have admin privileges")
                logging.error(f"Response details: {response.text}")
                return None
                
            response.raise_for_status()
            result = response.json()
            logging.info(f"Upload successful: {result}")
            return result
        except Exception as e:
            logging.error(f"Failed to upload data: {str(e)}", exc_info=True)
            return None

    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/admin/stats",
                headers=self._get_headers()
            )
            if response.status_code == 401:
                logging.error("Unauthorized - token may have expired")
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to get system stats: {str(e)}")
            return None
