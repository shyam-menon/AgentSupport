import pandas as pd
from fastapi import UploadFile
from typing import Dict, List
from src.services.embedding import EmbeddingService
from src.db.vector_store import VectorStore

class AdminService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    async def process_csv_file(self, file: UploadFile) -> Dict:
        """
        Process uploaded CSV file and store in vector database
        """
        try:
            # Read CSV file
            df = pd.read_csv(file.file)
            
            # Process in chunks of 50
            chunk_size = 50
            total_processed = 0
            
            for i in range(0, len(df), chunk_size):
                chunk = df[i:i + chunk_size]
                
                # Generate embeddings for descriptions
                descriptions = chunk['description'].tolist()
                embeddings = await self.embedding_service.batch_generate_embeddings(descriptions)
                
                # Prepare records for vector store
                records = []
                for j, row in chunk.iterrows():
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
                        "embedding": embeddings[j]
                    }
                    records.append(record)
                
                # Store in vector database
                await self.vector_store.add_records(records)
                total_processed += len(chunk)
            
            return {"total_processed": total_processed}
            
        except Exception as e:
            raise Exception(f"Error processing CSV file: {str(e)}")

    async def get_system_stats(self) -> Dict:
        """
        Get system statistics
        """
        try:
            stats = await self.vector_store.get_stats()
            return {
                "total_tickets": stats["total_records"],
                "vector_dimensions": stats["embedding_dim"],
                "last_updated": stats["last_updated"]
            }
        except Exception as e:
            raise Exception(f"Error fetching system stats: {str(e)}")
