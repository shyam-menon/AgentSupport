from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings
from src.core.config import settings
import numpy as np
from datetime import datetime

class VectorStore:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        ))
        self.collection = self.client.get_or_create_collection(
            name="support_tickets",
            metadata={"hnsw:space": "cosine"}
        )

    async def add_records(self, records: List[Dict]):
        """
        Add records to the vector store
        """
        try:
            documents = []
            embeddings = []
            metadatas = []
            ids = []

            for record in records:
                # Extract embedding
                embedding = record.pop("embedding")
                
                # Prepare document and metadata
                documents.append(record["description"])
                embeddings.append(embedding)
                metadatas.append({
                    "id": str(record["id"]),
                    "title": record["title"],
                    "issue_type": record.get("issue_type", ""),
                    "affected_system": record.get("affected_system", ""),
                    "status": record["status"],
                    "resolution": record.get("resolution", ""),
                    "steps": "|".join(record.get("steps", [])),
                    "created_at": str(record["created_at"]),
                    "updated_at": str(record["updated_at"])
                })
                ids.append(str(record["id"]))

            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            # Persist changes
            self.client.persist()
            
        except Exception as e:
            raise Exception(f"Error adding records to vector store: {str(e)}")

    async def search(
        self,
        query_embedding: np.ndarray,
        filter_criteria: Optional[Dict] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search for similar vectors
        """
        try:
            # Prepare filter
            where_clause = {}
            if filter_criteria:
                for key, value in filter_criteria.items():
                    if value:
                        where_clause[key] = value

            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                where=where_clause if where_clause else None,
                n_results=limit
            )

            # Process results
            processed_results = []
            for i in range(len(results["ids"][0])):
                metadata = results["metadatas"][0][i]
                processed_results.append({
                    "id": int(metadata["id"]),
                    "title": metadata["title"],
                    "description": results["documents"][0][i],
                    "issue_type": metadata.get("issue_type"),
                    "affected_system": metadata.get("affected_system"),
                    "status": metadata["status"],
                    "resolution": metadata.get("resolution"),
                    "steps": metadata.get("steps", "").split("|") if metadata.get("steps") else [],
                    "created_at": datetime.fromisoformat(metadata["created_at"]),
                    "updated_at": datetime.fromisoformat(metadata["updated_at"])
                })

            return processed_results

        except Exception as e:
            raise Exception(f"Error searching in vector store: {str(e)}")

    async def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        """
        try:
            collection_stats = self.collection.count()
            return {
                "total_records": collection_stats,
                "embedding_dim": 1536,  # text-embedding-ada-002 dimension
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error getting vector store stats: {str(e)}")
