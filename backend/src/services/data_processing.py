from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
from src.services.embedding import EmbeddingService
from src.db.vector_store import VectorStore

class DataProcessingService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    async def process_csv(self, file_path: str, chunk_size: int = 50) -> Dict[str, Any]:
        """
        Process a CSV file containing support tickets
        Args:
            file_path: Path to the CSV file
            chunk_size: Number of records to process at once
        Returns:
            Dict containing processing statistics
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Basic validation
            required_columns = ['title', 'description', 'status']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # Initialize statistics
            stats = {
                "total_records": len(df),
                "processed_records": 0,
                "failed_records": 0,
                "start_time": datetime.now()
            }

            # Process in chunks
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                
                try:
                    # Prepare texts for embedding
                    texts = [
                        f"Title: {row['title']}\nDescription: {row['description']}"
                        for _, row in chunk.iterrows()
                    ]
                    
                    # Generate embeddings
                    embeddings = await self.embedding_service.batch_generate_embeddings(texts)
                    
                    # Prepare records for vector store
                    records = []
                    for j, (_, row) in enumerate(chunk.iterrows()):
                        record = {
                            "id": row.get('id', i + j),  # Use provided ID or generate one
                            "title": row['title'],
                            "description": row['description'],
                            "issue_type": row.get('issue_type', ''),
                            "affected_system": row.get('affected_system', ''),
                            "status": row['status'],
                            "resolution": row.get('resolution', ''),
                            "steps": row.get('steps', '').split('|') if row.get('steps') else [],
                            "created_at": row.get('created_at', datetime.now()),
                            "updated_at": row.get('updated_at', datetime.now()),
                            "embedding": embeddings[j]
                        }
                        records.append(record)
                    
                    # Add to vector store
                    await self.vector_store.add_records(records)
                    
                    stats["processed_records"] += len(chunk)
                    
                except Exception as e:
                    print(f"Error processing chunk {i//chunk_size}: {str(e)}")
                    stats["failed_records"] += len(chunk)

            # Calculate final statistics
            stats["end_time"] = datetime.now()
            stats["processing_time"] = (stats["end_time"] - stats["start_time"]).total_seconds()
            stats["success_rate"] = (stats["processed_records"] / stats["total_records"]) * 100
            
            return stats
            
        except Exception as e:
            raise Exception(f"Error processing CSV file: {str(e)}")

    async def validate_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a CSV file before processing
        Args:
            file_path: Path to the CSV file
        Returns:
            Dict containing validation results
        """
        try:
            df = pd.read_csv(file_path)
            
            validation_results = {
                "is_valid": True,
                "total_records": len(df),
                "columns_present": list(df.columns),
                "issues": []
            }
            
            # Check required columns
            required_columns = ['title', 'description', 'status']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                validation_results["is_valid"] = False
                validation_results["issues"].append(f"Missing required columns: {missing_columns}")
            
            # Check for empty values in required fields
            for col in required_columns:
                if col in df.columns and df[col].isna().any():
                    validation_results["is_valid"] = False
                    empty_count = df[col].isna().sum()
                    validation_results["issues"].append(f"Found {empty_count} empty values in {col}")
            
            return validation_results
            
        except Exception as e:
            return {
                "is_valid": False,
                "issues": [f"Error validating CSV file: {str(e)}"]
            }
