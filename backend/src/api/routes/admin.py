from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from src.schemas.ticket import Ticket
from src.services.admin import AdminService
from src.api.dependencies import get_current_admin_user

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
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
    
    try:
        result = await admin_service.process_csv_file(file)
        return {"message": "File processed successfully", "processed_records": result}
    except Exception as e:
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
    try:
        stats = await admin_service.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stats: {str(e)}"
        )
