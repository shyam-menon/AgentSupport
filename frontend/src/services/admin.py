import os
from datetime import datetime
import logging
import pandas as pd

class AdminService:
    def __init__(self):
        """Initialize admin service"""
        self.api_client = None
        if "api_client" in globals():
            self.api_client = globals()["api_client"]

    def get_stats(self):
        """Get system statistics"""
        try:
            # Get stats from API
            response = self.api_client.get_system_stats()
            
            if not response:
                return {
                    "total_documents": 0,
                    "markdown_files": 0,
                    "embedding_count": 0,
                    "last_updated": "Never",
                    "vector_store_healthy": False
                }
            
            # Extract stats from response
            vector_store = response.get("vector_store", {})
            markdown_files = response.get("markdown_files", {})
            
            return {
                "total_documents": vector_store.get("total_records", 0),
                "markdown_files": markdown_files.get("total_files", 0),
                "embedding_count": vector_store.get("total_embeddings", 0),
                "last_updated": vector_store.get("last_updated", "Never"),
                "vector_store_healthy": vector_store.get("has_data", False),
                "storage_info": {
                    "markdown_size_mb": markdown_files.get("total_size_mb", 0),
                    "vector_store_size_mb": vector_store.get("total_size_mb", 0)
                },
                "sample_records": [vector_store.get("sample_metadata", {})]
            }
            
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {
                "total_documents": 0,
                "markdown_files": 0,
                "embedding_count": 0,
                "last_updated": "Never",
                "vector_store_healthy": False
            }

    def process_csv_file(self, file):
        """Process uploaded CSV file"""
        try:
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
            
            if response and response.get("status") == "success":
                return {
                    "success": True,
                    "message": f"Processed {len(df)} rows successfully"
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "Unknown error occurred")
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
