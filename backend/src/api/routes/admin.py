from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from src.schemas.ticket import Ticket
from src.services.admin import AdminService
from src.api.dependencies import get_current_admin_user
import logging

router = APIRouter()

@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    current_admin = Depends(get_current_admin_user),
    admin_service: AdminService = Depends()
):
    """
    Upload and process CSV data file
    """
    logging.info(f"Upload request received from admin user: {current_admin.email}")
    logging.info(f"File name: {file.filename}")
    
    if not file.filename.endswith('.csv'):
        logging.error(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
    
    try:
        logging.info("Starting file processing")
        result = await admin_service.process_csv_file(file)
        logging.info(f"File processing completed: {result}")
        return result
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/stats")
async def get_system_stats(
    current_admin = Depends(get_current_admin_user),
    admin_service: AdminService = Depends()
):
    """
    Get system statistics
    """
    logging.info(f"Stats request received from admin user: {current_admin.email}")
    try:
        stats = await admin_service.get_system_stats()
        logging.info(f"Stats retrieved: {stats}")
        return stats
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting system stats: {str(e)}"
        )

@router.get("/debug/vector-store")
async def get_vector_store_debug():
    """Get debug information about the vector store"""
    try:
        admin_service = AdminService()
        store_stats = admin_service.vector_store.get_stats()
        
        # Get collection info
        collection_data = admin_service.vector_store.collection.get()
        
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
