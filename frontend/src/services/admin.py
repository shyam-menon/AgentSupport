import os
from datetime import datetime
import logging
import pandas as pd
from typing import Dict
import streamlit as st
from src.utils.api_client import APIClient

class AdminService:
    def __init__(self):
        """Initialize admin service"""
        self.api_client = st.session_state.get("api_client")
        if not self.api_client:
            self.api_client = APIClient()
            st.session_state["api_client"] = self.api_client

    def get_stats(self) -> Dict:
        """Get system statistics"""
        try:
            if not self.api_client:
                raise ValueError("API client not initialized")
                
            # Get stats from API
            response = self.api_client.get_system_stats()
            
            if not response:
                return {
                    "total_documents": 0,
                    "markdown_files": 0,
                    "embedding_count": 0,
                    "last_updated": "Never",
                    "vector_store_healthy": False,
                    "storage_info": {
                        "markdown_size_mb": 0,
                        "vector_store_size_mb": 0
                    }
                }
            
            return response
            
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {
                "total_documents": 0,
                "markdown_files": 0,
                "embedding_count": 0,
                "last_updated": "Never",
                "vector_store_healthy": False,
                "storage_info": {
                    "markdown_size_mb": 0,
                    "vector_store_size_mb": 0
                }
            }

    def process_csv_file(self, file) -> Dict:
        """Process uploaded CSV file"""
        try:
            if not self.api_client:
                raise ValueError("API client not initialized")
                
            # Read CSV file to verify it's valid
            df = pd.read_csv(file)
            if df.empty:
                return {
                    "success": False,
                    "error": "CSV file is empty"
                }
            
            # Reset file pointer for upload
            file.seek(0)
            
            # Upload to backend
            response = self.api_client.upload_data(file)
            
            if not response:
                return {
                    "success": False,
                    "error": "Failed to upload file"
                }
                
            return {
                "success": True,
                "processed_records": len(df)
            }
            
        except Exception as e:
            logging.error(f"Error processing CSV file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def upload_data(self, file):
        """Upload data file to backend"""
        try:
            response = self.api_client.upload_data(file)
            return response
        except Exception as e:
            logging.error(f"Error uploading data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def clear_embeddings(self) -> Dict:
        """Clear all embeddings from the vector store"""
        try:
            if not self.api_client:
                raise ValueError("API client not initialized")
                
            response = self.api_client.post("/admin/clear-embeddings")
            if not response:
                return {
                    "success": False,
                    "error": "Failed to clear embeddings"
                }
                
            return {
                "success": True
            }
            
        except Exception as e:
            logging.error(f"Error clearing embeddings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
