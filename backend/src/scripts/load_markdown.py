import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the parent directory to sys.path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

from db.vector_store import VectorStore
from datetime import datetime

async def load_markdown_files():
    """Load markdown files into vector store"""
    vector_store = VectorStore()
    markdown_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "markdown")
    
    if not os.path.exists(markdown_dir):
        logging.error(f"Markdown directory not found: {markdown_dir}")
        return
    
    # Get all markdown files
    markdown_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
    if not markdown_files:
        logging.error("No markdown files found")
        return
    
    logging.info(f"Found {len(markdown_files)} markdown files")
    records = []
    
    # Process each file
    for file in markdown_files:
        file_path = os.path.join(markdown_dir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create record
            record = {
                "content": content,
                "metadata": {
                    "source": file,
                    "id": int(file.split('_')[1]),  # Get ID from filename (chunk_ID_timestamp.md)
                    "title": f"Support Ticket {file.split('_')[1]}",
                    "status": "resolved",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            }
            records.append(record)
            
        except Exception as e:
            logging.error(f"Error processing file {file}: {e}")
    
    if records:
        try:
            # Add records to vector store
            await vector_store.add_records(records)
            logging.info(f"Successfully loaded {len(records)} records into vector store")
        except Exception as e:
            logging.error(f"Error adding records to vector store: {e}")
    else:
        logging.error("No valid records to add")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(load_markdown_files())
