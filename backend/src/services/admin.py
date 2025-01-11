import pandas as pd
import tempfile
from fastapi import UploadFile
from typing import Dict, List
from src.services.embedding import EmbeddingService
from src.db.vector_store import VectorStore
from src.services.markdown_converter import MarkdownConverter

class AdminService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.markdown_converter = MarkdownConverter()

    async def process_csv_file(self, file: UploadFile) -> Dict:
        """
        Process uploaded CSV file:
        1. Save to temporary file
        2. Convert to markdown files
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

            # Convert CSV to markdown files
            markdown_files = await self.markdown_converter.convert_csv_to_markdown(temp_file_path)
            
            total_processed = 0
            for markdown_file in markdown_files:
                # Read markdown content
                content = self.markdown_converter.get_markdown_content(markdown_file)
                
                # Generate embedding
                embedding = await self.embedding_service.generate_embedding(content)
                
                # Read original CSV data for this chunk
                df = pd.read_csv(temp_file_path)
                chunk_start = total_processed
                chunk_end = min(total_processed + self.markdown_converter.chunk_size, len(df))
                chunk = df.iloc[chunk_start:chunk_end]
                
                # Prepare records for vector store
                records = []
                for _, row in chunk.iterrows():
                    record = {
                        "id": row.get("id"),
                        "title": row.get("title"),
                        "description": row.get("description"),
                        "issue_type": row.get("issue_type"),
                        "affected_system": row.get("affected_system"),
                        "status": row.get("status"),
                        "resolution": row.get("resolution"),
                        "steps": row.get("steps", "").split("|") if pd.notna(row.get("steps")) else [],
                        "created_at": row.get("created_at"),
                        "updated_at": row.get("updated_at"),
                        "embedding": embedding
                    }
                    records.append(record)
                
                # Store in vector database
                await self.vector_store.add_records(records)
                total_processed += len(chunk)
            
            # Cleanup
            self.markdown_converter.cleanup_markdown_files(markdown_files)
            
            return {
                "total_processed": total_processed,
                "markdown_files_generated": len(markdown_files)
            }
            
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

    async def get_system_stats(self) -> Dict:
        """
        Get system statistics
        """
        try:
            # Get collection stats from vector store
            collection_stats = await self.vector_store.get_stats()
            
            return {
                "total_documents": collection_stats.get("total_documents", 0),
                "last_updated": collection_stats.get("last_updated")
            }
        except Exception as e:
            raise Exception(f"Error getting system stats: {str(e)}")
