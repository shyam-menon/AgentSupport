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
            # Log the number of records and first record as sample
            logging.info(f"Adding {len(records)} records to vector store")
            if records:
                logging.info(f"Sample record metadata: {records[0]['metadata']}")
            
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
                record_id = self._generate_id(i)
                ids.append(record_id)
                logging.debug(f"Prepared record {i+1}/{len(records)} with ID: {record_id}")
            
            # Log collection state before adding
            before_count = self.collection.count()
            logging.info(f"Collection count before adding: {before_count}")
            
            # Add to collection - ChromaDB will generate embeddings automatically
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Verify records were added
            after_count = self.collection.count()
            added_count = after_count - before_count
            logging.info(f"Added {added_count} records. Collection count: {after_count}")
            
            # Update stats
            stats = self._update_stats()
            logging.info(f"Updated vector store stats: {stats}")
            
        except Exception as e:
            logging.error(f"Error adding records: {e}")
            raise Exception(f"Error adding records to vector store: {str(e)}")

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
            # Log collection info and data
            logging.info("=== DEBUG: Collection Contents ===")
            collection_data = self.collection.get()
            logging.info(f"Total items in collection: {len(collection_data['ids']) if collection_data['ids'] else 0}")
            if collection_data['ids']:
                logging.info("Sample metadata fields:")
                for i, metadata in enumerate(collection_data['metadatas'][:2]):  # Show first 2 items
                    logging.info(f"Item {i + 1} metadata: {metadata}")
                    logging.info(f"Item {i + 1} content preview: {collection_data['documents'][i][:200]}...")
            
            # Log search parameters
            logging.info("=== DEBUG: Search Parameters ===")
            logging.info(f"Query embedding shape: {query_embedding.shape}")
            logging.info(f"Filter criteria: {filter_criteria}")
            
            # Prepare filter
            where_clause = None
            if filter_criteria:
                # Build a list of valid conditions
                conditions = []
                for key, value in filter_criteria.items():
                    if value:
                        # For each field, check both exact match and "Not specified"
                        field_variations = [
                            key,  # Original
                            key.lower(),  # Lowercase
                            key.replace(' ', '_'),  # Replace space with underscore
                            key.lower().replace(' ', '_')  # Both
                        ]
                        
                        # Create conditions for both exact match and "Not specified"
                        field_matches = []
                        for field in field_variations:
                            field_matches.extend([
                                {field: {"$eq": value}},  # Exact match
                                {field: {"$eq": "Not specified"}}  # Default value
                            ])
                        
                        field_condition = {"$or": field_matches}
                        conditions.append(field_condition)
                
                # Combine conditions if we have any
                if conditions:
                    if len(conditions) == 1:
                        where_clause = conditions[0]
                    else:
                        where_clause = {"$and": conditions}

            # Log the final query
            logging.info("=== DEBUG: Final Query ===")
            logging.info(f"Where clause: {where_clause}")

            # Convert numpy array to list for ChromaDB
            embedding_list = query_embedding.tolist()

            # Perform search
            results = self.collection.query(
                query_embeddings=[embedding_list],
                where=where_clause,
                n_results=limit
            )
            
            # Log raw results
            logging.info("=== DEBUG: Raw Search Results ===")
            num_results = len(results['ids'][0]) if results['ids'] and results['ids'][0] else 0
            logging.info(f"Got {num_results} results")
            if num_results > 0:
                logging.info(f"First result metadata: {results['metadatas'][0][0]}")
                logging.info(f"First result content preview: {results['documents'][0][0][:200]}...")
            
            # Process results
            processed_results = []
            if results["ids"] and results["ids"][0]:  # Check if we have any results
                for i in range(len(results["ids"][0])):
                    metadata = results["metadatas"][0][i]
                    document = results["documents"][0][i]
                    
                    # Parse dates using the helper function
                    created_at = self._parse_date(metadata.get("Created", metadata.get("created", datetime.now().isoformat())))
                    updated_at = self._parse_date(metadata.get("Updated", metadata.get("updated", datetime.now().isoformat())))

                    # Create ticket from available metadata
                    ticket_data = {
                        "id": metadata.get("chunk_id", f"unknown_{i}"),
                        "title": metadata.get("Summary", "No Title"),
                        "description": document,  # Use the full document content
                        "Issue Type": metadata.get("Issue Type", metadata.get("issue_type", metadata.get("type"))),
                        "Affected System": metadata.get("Affected System", metadata.get("affected_system", metadata.get("system"))),
                        "status": metadata.get("Status", "Unknown"),
                        "resolution": metadata.get("Resolution", ""),
                        "steps": metadata.get("Steps", "").split("|") if metadata.get("Steps") else [],
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                    processed_results.append(ticket_data)
            
            logging.info(f"Processed {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            logging.error(f"Error in search: {str(e)}", exc_info=True)
            return []

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
