from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.schemas.ticket import TicketSearch, Ticket
from src.services.search import SearchService
from src.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=List[Ticket])
async def search_tickets(
    query: TicketSearch,
    current_user = Depends(get_current_user),
    search_service: SearchService = Depends()
):
    """
    Search for similar tickets based on description and optional filters
    """
    try:
        results = await search_service.search_similar_tickets(
            description=query.description,
            issue_type=query.issue_type,
            affected_system=query.affected_system,
            limit=query.num_results
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )
