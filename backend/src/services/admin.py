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

    async def process_csv_file(self, file: UploadFile) -> Dict:
        """
        Process uploaded CSV file
        """
        temp_file_path = None
        try:
            logging.info(f"Starting to process CSV file: {file.filename}")
            
            # Save uploaded file to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                temp_file_path = temp_file.name
                content = await file.read()
                temp_file.write(content)
            logging.info(f"Saved CSV to temporary file: {temp_file_path}")
            
            # Read CSV file
            df = pd.read_csv(temp_file_path)
            if df.empty:
                raise Exception("CSV file is empty")
            logging.info(f"Successfully read CSV with {len(df)} rows and {len(df.columns)} columns")
            logging.info(f"CSV columns: {df.columns.tolist()}")
            
            # Convert to markdown
            logging.info("Converting DataFrame to markdown chunks...")
            markdown_chunks = self.markdown_converter.convert_dataframe(df)
            if not markdown_chunks:
                raise Exception("No content generated from CSV")
            logging.info(f"Generated {len(markdown_chunks)} markdown chunks")
            
            # Save markdown chunks to files
            markdown_files = []
            logging.info(f"Saving markdown chunks to directory: {self.markdown_dir}")
            for i, chunk in enumerate(markdown_chunks, 1):
                chunk_file = os.path.join(self.markdown_dir, f"chunk_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                markdown_files.append(chunk_file)
                logging.info(f"Saved chunk {i}/{len(markdown_chunks)} to {chunk_file}")
            
            # Add to vector store
            total_chunks = len(markdown_chunks)
            records = []
            
            for i, (chunk, markdown_file) in enumerate(zip(markdown_chunks, markdown_files), 1):
                logging.info(f"Processing chunk {i}/{total_chunks} for vector store")
                
                # Parse the chunk to extract metadata
                lines = chunk.split('\n')
                metadata = {
                    "source": file.filename,
                    "chunk_id": f"chunk_{i}",
                    "total_chunks": total_chunks,
                    "processed_at": datetime.now().isoformat(),
                    "markdown_file": os.path.basename(markdown_file)
                }
                
                # Extract fields from the chunk content
                current_field = None
                field_content = []
                for line in lines:
                    if line.startswith('### '):
                        # If we were collecting a field, save it
                        if current_field and field_content:
                            field_value = '\n'.join(field_content).strip()
                            if field_value:
                                # Store field in multiple formats to improve matching
                                metadata[current_field] = field_value  # Original
                                metadata[current_field.lower()] = field_value  # Lowercase
                                metadata[current_field.replace(' ', '_')] = field_value  # With underscores
                                metadata[current_field.lower().replace(' ', '_')] = field_value  # Lowercase with underscores
                            field_content = []
                        # Start new field
                        current_field = line[4:].strip()
                    elif current_field and line.strip():
                        field_content.append(line.strip())
                
                # Save the last field if any
                if current_field and field_content:
                    field_value = '\n'.join(field_content).strip()
                    if field_value:
                        # Store field in multiple formats to improve matching
                        metadata[current_field] = field_value  # Original
                        metadata[current_field.lower()] = field_value  # Lowercase
                        metadata[current_field.replace(' ', '_')] = field_value  # With underscores
                        metadata[current_field.lower().replace(' ', '_')] = field_value  # Lowercase with underscores

                # Add standard fields that should always be present
                standard_fields = [
                    "Issue Type",
                    "Affected System",
                    "Priority",
                    "Status",
                    "Summary"
                ]
                
                # Ensure all standard fields exist in metadata
                for field in standard_fields:
                    if field not in metadata:
                        # Try to find the field in different formats
                        field_variations = [
                            field,
                            field.lower(),
                            field.replace(' ', '_'),
                            field.lower().replace(' ', '_')
                        ]
                        # Find first matching variation
                        for var in field_variations:
                            if var in metadata:
                                metadata[field] = metadata[var]
                                break
                        # If still not found, set to default
                        if field not in metadata:
                            metadata[field] = "Not specified"

                logging.info(f"Extracted metadata for chunk {i}: {metadata}")
                
                # Create record with content and metadata
                record = {
                    "content": chunk,
                    "metadata": metadata
                }
                records.append(record)
            
            # Add all records at once
            logging.info(f"Adding {len(records)} records to vector store...")
            await self.vector_store.add_records(records)
            logging.info("Successfully added records to vector store")
            
            return {
                "status": "success",
                "total_processed": total_chunks,
                "message": f"Successfully processed {total_chunks} chunks",
                "markdown_files": [os.path.basename(f) for f in markdown_files]
            }
            
        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            raise Exception(f"Error processing file: {str(e)}")
        
        finally:
            # Clean up temp file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

    async def get_system_stats(self) -> Dict:
        """
        Get system statistics
        """
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_stats()
            
            # Get markdown directory stats
            markdown_size = 0
            markdown_count = self._count_markdown_files()
            if os.path.exists(self.markdown_dir):
                markdown_size = get_directory_size(self.markdown_dir)
            
            # Get vector store directory size
            vector_store_size = 0
            vector_store_dir = self.vector_store.get_store_path()
            if os.path.exists(vector_store_dir):
                vector_store_size = get_directory_size(vector_store_dir)
            
            # Format stats
            stats = {
                "status": "success",
                "vector_store": {
                    "total_records": vector_stats.get("total_records", 0),
                    "total_embeddings": vector_stats.get("embedding_count", 0),
                    "last_updated": vector_stats.get("last_updated", "Never"),
                    "has_data": vector_stats.get("healthy", False),
                    "total_size_mb": vector_store_size / (1024 * 1024),
                    "sample_metadata": vector_stats.get("sample_records", [{}])[0].get("metadata", {}) if vector_stats.get("sample_records") else {}
                },
                "markdown_files": {
                    "total_files": markdown_count,
                    "total_size_mb": markdown_size / (1024 * 1024)
                }
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting system stats: {str(e)}")
            return {
                "status": "error",
                "vector_store": {
                    "total_records": 0,
                    "total_embeddings": 0,
                    "last_updated": "Never",
                    "has_data": False,
                    "total_size_mb": 0,
                    "sample_metadata": {}
                },
                "markdown_files": {
                    "total_files": 0,
                    "total_size_mb": 0
                }
            }
