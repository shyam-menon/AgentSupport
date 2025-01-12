from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Dict
from src.schemas.ticket import Ticket
from src.services.admin import AdminService
from src.api.dependencies import get_current_admin_user, get_vector_store, get_current_user
from src.schemas.user import User
from src.db.vector_store import VectorStore
import logging

router = APIRouter()

@router.get("/stats", response_model=Dict)
def get_stats(
    current_admin: User = Depends(get_current_admin_user)
) -> Dict:
    """Get system statistics"""
    try:
        admin_service = AdminService()
        stats = admin_service.get_stats()
        return stats
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )

@router.post("/clear-embeddings", response_model=Dict[str, bool])
def clear_embeddings(
    current_admin: User = Depends(get_current_admin_user),
    vector_store: VectorStore = Depends(get_vector_store)
) -> Dict[str, bool]:
    """Clear all embeddings from the vector store"""
    try:
        success = vector_store.clear_all_data()
        return {"success": success}
    except Exception as e:
        logging.error(f"Error clearing embeddings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing embeddings: {str(e)}"
        )

@router.post("/upload", response_model=Dict)
def upload_file(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin_user)
) -> Dict:
    """Upload and process a file"""
    try:
        admin_service = AdminService()
        result = admin_service.process_file(file)
        return result
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/debug/vector-store")
async def get_vector_store_debug(
    vector_store: VectorStore = Depends(get_vector_store)
):
    """Get debug information about the vector store"""
    try:
        admin_service = AdminService()
        store_stats = vector_store.get_stats()
        
        # Get collection info
        collection_data = vector_store.collection.get()
        
        debug_info = {
            "stats": store_stats,
            "collection_info": {
                "total_items": len(collection_data["ids"]) if collection_data["ids"] else 0,
                "sample_items": []
            }
        }
        
        # Add sample items
        if collection_data["ids"] and len(collection_data["ids"]) > 0:
            for i in range(min(2, len(collection_data["ids"]))):
                sample_item = {
                    "id": collection_data["ids"][i],
                    "metadata": collection_data["metadatas"][i],
                    "document_preview": collection_data["documents"][i][:200] + "..."
                }
                debug_info["collection_info"]["sample_items"].append(sample_item)
        
        return debug_info
    except Exception as e:
        logging.error(f"Error getting vector store debug info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
