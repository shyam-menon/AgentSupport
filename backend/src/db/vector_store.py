from typing import Dict, List, Optional
import chromadb
from src.core.config import settings
import numpy as np
from datetime import datetime
import logging
import os
import json
from src.services.embedding import EmbeddingService

class AzureOpenAIEmbeddingFunction:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        
    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        Generate embeddings for input texts
        Args:
            input: List of texts to generate embeddings for
        Returns:
            List of embeddings as float lists
        """
        if isinstance(input, str):
            input = [input]
        
        try:
            embeddings = self.embedding_service.batch_generate_embeddings_sync(input)
            return [e.tolist() for e in embeddings]
        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            raise

class VectorStore:
    def __init__(self):
        # Ensure the ChromaDB directory exists
        chroma_dir = settings.CHROMA_PERSIST_DIRECTORY
        if not os.path.exists(chroma_dir):
            logging.info(f"Creating ChromaDB directory: {chroma_dir}")
            os.makedirs(chroma_dir, exist_ok=True)
        
        logging.info(f"Initializing ChromaDB with persist directory: {chroma_dir}")
        
        # Initialize embedding service
        self.embedding_service = EmbeddingService()
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=chromadb.Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name="support_tickets",
            metadata={"hnsw:space": "cosine", "dimension": 1536},  # Azure OpenAI dimension
            embedding_function=AzureOpenAIEmbeddingFunction()
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

    def _update_stats(self) -> Dict:
        """Update stats from collection"""
        try:
            stats = self._load_stats()
            
            # Get collection data safely
            try:
                # Get collection count
                count = self.collection.count()
                
                # Update stats
                stats.update({
                    "total_records": count,
                    "embedding_count": count,  # Each record has one embedding
                    "last_updated": datetime.now().isoformat(),
                    "healthy": True
                })
                
                # Save updated stats
                self._save_stats(stats)
                
                return stats
                
            except Exception as e:
                logging.error(f"Error getting collection data: {e}")
                stats.update({
                    "healthy": False,
                    "last_error": str(e)
                })
                return stats
                
        except Exception as e:
            logging.error(f"Error updating stats: {e}")
            return {
                "total_records": 0,
                "embedding_count": 0,
                "last_updated": None,
                "healthy": False,
                "last_error": str(e)
            }

    def _generate_id(self, index: int) -> str:
        """Generate a unique ID for a record"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"doc_{index}_{timestamp}"

    async def add_records(self, records: List[Dict]):
        """Add records to the vector store"""
        try:
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for i, record in enumerate(records):
                record_id = str(record.get('id', f'gen_{i}'))
                ids.append(record_id)
                embeddings.append(record['embedding'])
                
                # Create document text combining title and description
                doc_text = f"Title: {record['title']}\nDescription: {record['description']}"
                documents.append(doc_text)
                
                # Prepare metadata including all fields
                metadata = {
                    'id': record_id,
                    'Summary': record['title'],
                    'Issue Type': record.get('issue_type', ''),
                    'Affected System': record.get('affected_system', ''),
                    'Status': record.get('status', ''),
                    'Resolution': record.get('resolution', ''),
                    'Steps': '|'.join(record.get('steps', [])) if record.get('steps') else '',
                    'Created': record.get('created_at', '').isoformat() if isinstance(record.get('created_at'), datetime) else str(record.get('created_at', '')),
                    'Updated': record.get('updated_at', '').isoformat() if isinstance(record.get('updated_at'), datetime) else str(record.get('updated_at', ''))
                }
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            return len(ids)
            
        except Exception as e:
            logging.error(f"Error adding records to vector store: {str(e)}", exc_info=True)
            raise

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in various formats to datetime object."""
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                # Try DD-MM-YYYY HH:mm format
                return datetime.strptime(date_str, "%d-%m-%Y %H:%M")
            except ValueError:
                # Return current time if parsing fails
                return datetime.now()

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
            # Convert numpy array to list for ChromaDB
            embedding_list = query_embedding.tolist()
            
            # Prepare filter
            where_clause = None
            if filter_criteria:
                conditions = []
                for key, value in filter_criteria.items():
                    if value:
                        conditions.append({key: {"$eq": value}})
                
                if conditions:
                    where_clause = {"$and": conditions} if len(conditions) > 1 else conditions[0]
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[embedding_list],
                where=where_clause,
                n_results=limit
            )
            
            # Process results
            processed_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    metadata = results["metadatas"][0][i]
                    document = results["documents"][0][i]
                    
                    # Extract steps from metadata
                    steps = []
                    if metadata.get("Steps"):
                        steps = [step for step in metadata["Steps"].split("|") if step]
                    
                    # Create ticket data
                    ticket_data = {
                        "id": metadata.get("id", f"unknown_{i}"),
                        "title": metadata.get("Summary", "No Title"),
                        "description": document,
                        "issue_type": metadata.get("Issue Type", ""),
                        "affected_system": metadata.get("Affected System", ""),
                        "status": metadata.get("Status", "Unknown"),
                        "resolution": metadata.get("Resolution", ""),
                        "steps": steps,
                        "created_at": self._parse_date(metadata.get("Created", "")),
                        "updated_at": self._parse_date(metadata.get("Updated", ""))
                    }
                    processed_results.append(ticket_data)
            
            return processed_results
            
        except Exception as e:
            logging.error(f"Error in vector store search: {str(e)}", exc_info=True)
            raise

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

    def clear_all_data(self):
        """Clear all data from the vector store"""
        try:
            # Delete the collection
            self.client.delete_collection("support_tickets")
            
            # Recreate the collection
            self.collection = self.client.create_collection(
                name="support_tickets",
                metadata={"hnsw:space": "cosine", "dimension": 1536},  # Azure OpenAI dimension
                embedding_function=AzureOpenAIEmbeddingFunction()
            )
            
            logging.info("Successfully cleared all data from vector store")
            return True
        except Exception as e:
            logging.error(f"Error clearing vector store: {str(e)}", exc_info=True)
            raise
