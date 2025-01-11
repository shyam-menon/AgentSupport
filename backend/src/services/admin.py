import pandas as pd
import tempfile
import os
from fastapi import UploadFile
from typing import Dict, List
from src.services.embedding import EmbeddingService
from src.db.vector_store import VectorStore
from src.services.markdown_converter import MarkdownConverter

class AdminService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.markdown_converter = MarkdownConverter(chunk_size=50)  # Set chunk size to 50

    async def process_csv_file(self, file: UploadFile) -> Dict:
        """
        Process uploaded CSV file:
        1. Save to temporary file
        2. Convert to markdown files (chunked for token limit)
        3. Generate embeddings for each markdown file
        4. Store in vector database
        5. Clean up temporary files
        """
        try:
            # Save uploaded file to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name

            # Convert CSV to markdown files (chunked)
            markdown_files = await self.markdown_converter.convert_csv_to_markdown(temp_file_path)
            
            total_processed = 0
            for markdown_file in markdown_files:
                # Read markdown content
                content = self.markdown_converter.get_markdown_content(markdown_file)
                
                # Generate embedding
                embedding = await self.embedding_service.generate_embedding(content)
                
                # Read original CSV data for metadata
                df = pd.read_csv(temp_file_path)
                chunk_start = total_processed
                chunk_end = min(total_processed + self.markdown_converter.chunk_size, len(df))
                chunk = df.iloc[chunk_start:chunk_end]
                
                # Prepare records for vector store
                records = []
                for _, row in chunk.iterrows():
                    record = {
                        "id": row["Issue key"],
                        "content": content,
                        "embedding": embedding,
                        "metadata": {
                            "issue_type": row["Issue Type"],
                            "priority": row["Priority"],
                            "status": row["Status"],
                            "created": row["Created"],
                            "updated": row["Updated"],
                            "assignee": row["Assignee"],
                            "reporter": row["Reporter"]
                        }
                    }
                    records.append(record)
                
                # Store in vector database
                self.vector_store.add_records(records)
                total_processed += len(chunk)
            
            # Clean up
            self.markdown_converter.cleanup_markdown_files(markdown_files)
            os.remove(temp_file_path)
            
            return {
                "message": "File processed successfully",
                "total_processed": total_processed,
                "markdown_files_generated": len(markdown_files)
            }
            
        except Exception as e:
            # Clean up on error
            if 'temp_file_path' in locals():
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            if 'markdown_files' in locals():
                try:
                    self.markdown_converter.cleanup_markdown_files(markdown_files)
                except:
                    pass
            raise Exception(f"Error processing file: {str(e)}")

    async def get_system_stats(self) -> Dict:
        """
        Get system statistics
        """
        try:
            stats = self.vector_store.get_stats()
            return stats
        except Exception as e:
            raise Exception(f"Error getting system stats: {str(e)}")
