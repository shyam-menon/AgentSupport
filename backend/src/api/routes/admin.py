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
        return {"message": "File processed successfully", "processed_records": result}
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
