from typing import Dict, List, Optional
import chromadb
from src.core.config import settings
import numpy as np
from datetime import datetime
import logging
import os
import json

class VectorStore:
    def __init__(self):
        # Ensure the ChromaDB directory exists
        chroma_dir = settings.CHROMA_PERSIST_DIRECTORY
        if not os.path.exists(chroma_dir):
            logging.info(f"Creating ChromaDB directory: {chroma_dir}")
            os.makedirs(chroma_dir, exist_ok=True)
        
        logging.info(f"Initializing ChromaDB with persist directory: {chroma_dir}")
        self.client = chromadb.Client(chromadb.Settings(
            persist_directory=chroma_dir,
            anonymized_telemetry=False
        ))
        
        self.collection = self.client.get_or_create_collection(
            name="support_tickets",
            metadata={"hnsw:space": "cosine"}
        )
        logging.info(f"Connected to ChromaDB collection: {self.collection.name}")
        
        # Initialize stats file
        self.stats_file = os.path.join(chroma_dir, "stats.json")
        if not os.path.exists(self.stats_file):
            self._save_stats({
                "total_records": 0,
                "embedding_count": 0,
                "last_updated": None,
                "healthy": True,
                "sample_records": []
            })

    def get_store_path(self) -> str:
        """Get the vector store directory path"""
        return settings.CHROMA_PERSIST_DIRECTORY

    def _save_stats(self, stats: Dict):
        """Save stats to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f)
        except Exception as e:
            logging.error(f"Error saving stats: {e}")

    def _load_stats(self) -> Dict:
        """Load stats from file"""
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading stats: {e}")
            return {}

    def _update_stats(self):
        """Update stats from collection"""
        try:
            stats = self._load_stats()
            
            # Get collection data safely
            try:
                collection_data = self.collection.get()
                if collection_data is None:
                    collection_data = {}
            except Exception as e:
                logging.error(f"Error getting collection data: {e}")
                collection_data = {}
            
            # Get counts safely
            try:
                total_records = self.collection.count()
                embeddings = collection_data.get("embeddings", [])
                embedding_count = len(embeddings) if embeddings else total_records  # If embeddings not returned, assume 1:1
            except Exception as e:
                logging.error(f"Error getting counts: {e}")
                total_records = 0
                embedding_count = 0
            
            # Update stats safely
            stats["total_records"] = total_records
            stats["embedding_count"] = embedding_count
            stats["last_updated"] = datetime.now().isoformat()
            stats["healthy"] = True
            
            # Update sample records if we have data
            if collection_data and collection_data.get("documents"):
                sample_docs = collection_data["documents"][:3]  # Get up to 3 samples
                sample_meta = collection_data.get("metadatas", [{}] * len(sample_docs))
                
                stats["sample_records"] = [
                    {
                        "text": doc[:200] + "..." if len(doc) > 200 else doc,
                        "metadata": meta
                    }
                    for doc, meta in zip(sample_docs, sample_meta)
                ]
            else:
                stats["sample_records"] = []
            
            self._save_stats(stats)
            return stats
            
        except Exception as e:
            logging.error(f"Error updating stats: {e}")
            stats = {
                "total_records": 0,
                "embedding_count": 0,
                "last_updated": None,
                "healthy": False,
                "sample_records": []
            }
            self._save_stats(stats)
            return stats

    def _generate_id(self, index: int) -> str:
        """Generate a unique ID for a record"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"doc_{index}_{timestamp}"

    async def add_records(self, records: List[Dict]):
        """
        Add records to the vector store.
        PersistentClient automatically persists changes, no need to call persist() explicitly.
        """
        try:
            # Log the records for debugging
            logging.info(f"Adding records: {records}")
            
            # Extract text and metadata
            texts = []
            metadatas = []
            ids = []
            
            for i, record in enumerate(records):
                # Validate record
                if "content" not in record:
                    raise ValueError(f"Record {i} missing 'content' field")
                if "metadata" not in record:
                    raise ValueError(f"Record {i} missing 'metadata' field")
                
                # Get content and metadata
                content = record["content"]
                metadata = record["metadata"]
                
                # Add to lists
                texts.append(content)
                metadatas.append(metadata)
                ids.append(self._generate_id(i))
            
            # Add to collection - ChromaDB will generate embeddings automatically
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Update stats
            self._update_stats()
            
        except Exception as e:
            logging.error(f"Error adding records: {e}")
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
            logging.error(f"Error searching in vector store: {e}")
            raise Exception(f"Error searching in vector store: {str(e)}")

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        """
        try:
            # Update and return stats
            return self._update_stats()
            
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {
                "total_records": 0,
                "embedding_count": 0,
                "last_updated": None,
                "healthy": False,
                "sample_records": []
            }

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """Query the vector store"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format results
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            return [
                {
                    "text": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(documents, metadatas, distances)
            ]
            
        except Exception as e:
            logging.error(f"Error querying vector store: {e}")
            return []
