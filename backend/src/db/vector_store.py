from typing import Dict, List, Optional
import chromadb
from src.core.config import settings
import numpy as np
from datetime import datetime
import logging
import os

class VectorStore:
    def __init__(self):
        # Ensure the ChromaDB directory exists
        chroma_dir = settings.CHROMA_PERSIST_DIRECTORY
        if not os.path.exists(chroma_dir):
            logging.info(f"Creating ChromaDB directory: {chroma_dir}")
            os.makedirs(chroma_dir, exist_ok=True)
        
        logging.info(f"Initializing ChromaDB with persist directory: {chroma_dir}")
        self.client = chromadb.PersistentClient(
            path=chroma_dir
        )
        self.collection = self.client.get_or_create_collection(
            name="support_tickets",
            metadata={"hnsw:space": "cosine"}
        )
        logging.info(f"Connected to ChromaDB collection: {self.collection.name}")

    async def add_records(self, records: List[Dict]):
        """
        Add records to the vector store.
        PersistentClient automatically persists changes, no need to call persist() explicitly.
        """
        try:
            documents = []
            embeddings = []
            metadatas = []
            ids = []

            for record in records:
                # Extract embedding and content
                embedding = record["embedding"]
                content = record["metadata"]["content"]
                metadata = record["metadata"]
                record_id = record["id"]
                
                # Add to lists
                documents.append(content)
                embeddings.append(embedding)
                metadatas.append(metadata)
                ids.append(record_id)

            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
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
                    "title": metadata.get("title"),
                    "description": results["documents"][0][i],
                    "issue_type": metadata.get("issue_type"),
                    "affected_system": metadata.get("affected_system"),
                    "status": metadata.get("status"),
                    "resolution": metadata.get("resolution"),
                    "steps": metadata.get("steps", "").split("|") if metadata.get("steps") else [],
                    "created_at": datetime.fromisoformat(metadata.get("created_at")),
                    "updated_at": datetime.fromisoformat(metadata.get("updated_at"))
                })

            return processed_results

        except Exception as e:
            raise Exception(f"Error searching in vector store: {str(e)}")

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        """
        try:
            logging.info("Getting vector store stats...")
            count = self.collection.count()
            logging.info(f"Collection count: {count}")
            
            peek = self.collection.peek(limit=1)
            logging.info(f"Peek result: {peek}")
            
            stats = {
                "total_records": count,
                "last_updated": datetime.now().isoformat(),
                "has_data": count > 0,
                "sample_record": None,
                "collection_name": self.collection.name
            }
            
            if peek and peek['ids']:
                # Get a sample record to verify data structure
                stats["sample_record"] = {
                    "id": peek['ids'][0],
                    "metadata": peek['metadatas'][0] if peek['metadatas'] else None
                }
            
            logging.info(f"Final vector store stats: {stats}")
            return stats
            
        except Exception as e:
            logging.error(f"Error getting vector store stats: {str(e)}", exc_info=True)
            raise Exception(f"Error getting vector store stats: {str(e)}")
