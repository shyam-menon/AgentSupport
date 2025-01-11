import pandas as pd
import tempfile
import os
from fastapi import UploadFile
from typing import Dict, List
from src.services.embedding import EmbeddingService
from src.db.vector_store import VectorStore
from src.services.markdown_converter import MarkdownConverter
import logging

class AdminService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.markdown_converter = MarkdownConverter(chunk_size=50)  # Set chunk size to 50

    async def process_csv_file(self, file: UploadFile) -> Dict:
        """
        Process uploaded CSV file:
        1. Save to temporary file
        2. Convert to markdown files (chunked)
        3. Generate embeddings for each markdown chunk
        4. Store in vector database
        5. Clean up temporary files
        """
        try:
            # Save uploaded file to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            logging.info(f"Saved uploaded file to temporary path: {temp_file_path}")

            # Convert CSV to markdown files (chunked)
            markdown_files = await self.markdown_converter.convert_csv_to_markdown(temp_file_path)
            logging.info(f"Generated {len(markdown_files)} markdown files")
            
            total_processed = 0
            for markdown_file in markdown_files:
                # Get markdown content parts that fit within token limit
                content_parts = self.markdown_converter.get_markdown_content(markdown_file)
                logging.info(f"Processing {markdown_file} - split into {len(content_parts)} parts")
                
                for part_index, content in enumerate(content_parts):
                    # Generate embedding for this part
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    # Get metadata from the markdown file
                    metadata = {
                        "source": os.path.basename(markdown_file),
                        "chunk_number": int(os.path.basename(markdown_file).split('_')[1].split('.')[0]),
                        "part_number": part_index + 1,
                        "total_parts": len(content_parts),
                        "content": content
                    }
                    logging.info(f"Generated embedding for chunk {metadata['chunk_number']} part {metadata['part_number']}")
                    
                    # Add to vector store
                    await self.vector_store.add_records([{
                        "id": f"chunk_{total_processed + 1}_part_{part_index + 1}",
                        "embedding": embedding.tolist(),
                        "metadata": metadata
                    }])
                    logging.info(f"Added record to vector store: chunk_{total_processed + 1}_part_{part_index + 1}")
                    
                    total_processed += 1
            
            # Clean up temporary files
            os.unlink(temp_file_path)
            self.markdown_converter.cleanup_markdown_files(markdown_files)
            logging.info("Cleaned up temporary files")
            
            # Get final stats
            final_stats = self.vector_store.get_stats()
            logging.info(f"Final vector store stats: {final_stats}")
            
            return {
                "status": "success",
                "total_processed": total_processed,
                "message": f"Successfully processed {total_processed} chunks",
                "vector_store_stats": final_stats
            }
            
        except Exception as e:
            # Clean up temporary files in case of error
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
            if 'markdown_files' in locals():
                self.markdown_converter.cleanup_markdown_files(markdown_files)
            logging.error(f"Error processing file: {str(e)}", exc_info=True)
            raise Exception(f"Error processing file: {str(e)}")

    async def get_system_stats(self) -> Dict:
        """
        Get system statistics including vector store info
        """
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_stats()
            
            # Get markdown directory stats
            markdown_files = []
            if os.path.exists(self.markdown_converter.markdown_dir):
                markdown_files = [f for f in os.listdir(self.markdown_converter.markdown_dir) 
                                if f.endswith('.md')]
            
            stats = {
                "status": "success",
                "vector_store": {
                    "total_records": vector_stats["total_records"],
                    "last_updated": vector_stats["last_updated"],
                    "has_data": vector_stats["has_data"],
                    "sample_metadata": vector_stats.get("sample_record", {}).get("metadata", {})
                },
                "markdown_files": {
                    "total_files": len(markdown_files),
                    "files": markdown_files[:5]  # Show first 5 files as sample
                }
            }
            
            logging.info(f"System stats: {stats}")
            return stats
            
        except Exception as e:
            logging.error(f"Error getting system stats: {str(e)}", exc_info=True)
            raise Exception(f"Error getting system stats: {str(e)}")
