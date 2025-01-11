import requests
from typing import Dict, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8080")
        self.token = None

    def _get_headers(self):
        """Get headers with authentication token if available"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get_form_headers(self):
        """Get headers for form data with authentication token if available"""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user and store token
        Returns the response data if successful, None if failed
        """
        try:
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
                logging.error("Authentication failed - invalid credentials")
                return None
                
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            return data
            
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
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
            files = {"file": file}
            response = requests.post(
                f"{self.base_url}/admin/upload",
                files=files,
                headers=self._get_headers()
            )
            if response.status_code == 401:
                logging.error("Unauthorized - token may have expired")
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to upload data: {str(e)}")
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
