from src.core.config import settings
import os
from typing import Dict, List
import pandas as pd
from datetime import datetime
import logging
import tempfile
from fastapi import UploadFile
from src.db.vector_store import VectorStore
from src.services.markdown_converter import MarkdownConverter
from src.utils.file_utils import get_directory_size

class AdminService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.markdown_converter = MarkdownConverter()
        self.markdown_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "markdown")
        os.makedirs(self.markdown_dir, exist_ok=True)

    def _count_markdown_files(self) -> int:
        """Count markdown files recursively"""
        count = 0
        for root, _, files in os.walk(self.markdown_dir):
            count += sum(1 for f in files if f.endswith('.md'))
        return count

    def get_stats(self) -> Dict:
        """Get system statistics"""
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_stats()
            
            # Get file system stats
            markdown_count = self._count_markdown_files()
            markdown_size = get_directory_size(self.markdown_dir)
            vector_store_size = get_directory_size(settings.CHROMA_PERSIST_DIRECTORY)
            
            return {
                "total_records": vector_stats.get("total_records", 0),
                "embedding_count": vector_stats.get("embedding_count", 0),
                "markdown_files": markdown_count,
                "storage_info": {
                    "markdown_size_mb": markdown_size / (1024 * 1024),
                    "vector_store_size_mb": vector_store_size / (1024 * 1024)
                },
                "last_updated": datetime.now().isoformat(),
                "vector_store_healthy": True
            }
        except Exception as e:
            logging.error(f"Error getting stats: {str(e)}")
            raise

    def process_file(self, file: UploadFile) -> Dict:
        """Process uploaded file"""
        if not file.filename.endswith('.csv'):
            raise ValueError("Only CSV files are supported")
            
        temp_file_path = None
        try:
            # Save uploaded file to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                temp_file_path = temp_file.name
                content = file.file.read()
                temp_file.write(content)
            
            # Read CSV file
            df = pd.read_csv(temp_file_path)
            if df.empty:
                raise ValueError("CSV file is empty")
                
            # Convert to markdown
            markdown_chunks = self.markdown_converter.convert_dataframe(df)
            if not markdown_chunks:
                raise ValueError("No valid data found in CSV")
                
            # Add to vector store
            self.vector_store.add_records(markdown_chunks)
            
            return {
                "success": True,
                "processed_records": len(markdown_chunks)
            }
            
        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            raise
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
