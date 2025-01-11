from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TicketBase(BaseModel):
    title: str
    description: str
    issue_type: Optional[str] = None
    affected_system: Optional[str] = None
    status: str = "open"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(TicketBase):
    resolution: Optional[str] = None
    steps: Optional[List[str]] = None

class TicketInDBBase(TicketBase):
    id: int
    created_at: datetime
    updated_at: datetime
    resolution: Optional[str] = None
    steps: Optional[List[str]] = None

    class Config:
        from_attributes = True

class Ticket(TicketInDBBase):
    pass

class TicketSearch(BaseModel):
    description: str
    issue_type: Optional[str] = None
    affected_system: Optional[str] = None
    additional_details: Optional[str] = None
    num_results: int = 5
