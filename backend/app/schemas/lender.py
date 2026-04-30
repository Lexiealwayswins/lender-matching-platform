# app/schemas/lender.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, List
from datetime import datetime
from .program import LenderProgramResponse

class LenderCreate(BaseModel):
    """Create a new lender."""
    name: str = Field(..., example="Stearns Bank")
    description: Optional[str] = Field(None, example="Equipment Finance Credit Box")


class LenderUpdate(BaseModel):
    """Update an existing lender."""
    name: Optional[str] = None
    description: Optional[str] = None


class LenderResponse(BaseModel):
    """Response for lender information."""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
        
class LenderWithProgramsResponse(BaseModel):
    """Complete nested response for a lender including all programs and rules.
    
    This is the main model used by get_all_lenders() to return structured data.
    """
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    programs: List[LenderProgramResponse] = []

    model_config = ConfigDict(from_attributes=True)