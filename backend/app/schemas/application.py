from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class LoanApplicationCreate(BaseModel):
    """Schema for creating a new loan application."""
    business_name: str = Field(..., example="ABC Construction LLC")
    industry: str = Field(..., example="Construction")
    state: str = Field(..., example="TX")
    years_in_business: int = Field(..., gt=0, example=4)
    annual_revenue: Optional[int] = Field(None, example=850000)
    
    fico_score: int = Field(..., gt=300, lt=850, example=720)
    paynet_score: Optional[int] = Field(None, example=680)
    has_bankruptcy: bool = Field(False)
    bankruptcy_years_ago: Optional[int] = Field(None, example=6)
    highest_previous_debt: Optional[int] = Field(None, example=50000)
    
    requested_amount: int = Field(..., gt=0, example=75000)
    requested_term_months: Optional[int] = Field(60, example=48)
    equipment_type: str = Field(..., example="Excavator")
    equipment_age_years: Optional[int] = Field(None, example=2)
    equipment_mileage: Optional[int] = Field(None, example=1200)

    model_config = ConfigDict(        
        json_schema_extra = {
            "example": {
                "business_name": "ABC Construction LLC",
                "industry": "Construction",
                "state": "TX",
                "years_in_business": 4,
                "fico_score": 720,
                "requested_amount": 75000,
                "equipment_type": "Excavator"
            }
        }
    )


class LoanApplicationUpdate(BaseModel):
    """Schema for updating an existing loan application."""
    business_name: Optional[str] = Field(None, example="ABC Construction LLC")
    industry: Optional[str] = Field(None, example="Construction")
    state: Optional[str] = Field(None, example="TX")
    years_in_business: Optional[int] = Field(None, gt=0, example=4)
    annual_revenue: Optional[int] = Field(None, example=850000)
    
    fico_score: Optional[int] = Field(None, gt=300, lt=850, example=720)
    paynet_score: Optional[int] = Field(None, example=680)
    has_bankruptcy: Optional[bool] = Field(None)
    bankruptcy_years_ago: Optional[int] = Field(None, example=6)
    highest_previous_debt: Optional[int] = Field(None, example=50000)
    
    requested_amount: Optional[int] = Field(None, gt=0, example=75000)
    requested_term_months: Optional[int] = Field(None, example=48)
    equipment_type: Optional[str] = Field(None, example="Excavator")
    equipment_age_years: Optional[int] = Field(None, example=2)
    equipment_mileage: Optional[int] = Field(None, example=1200)
    
    # status is managed by workflow

class LoanApplicationResponse(BaseModel):
    """Response schema for loan application."""
    id: int
    application_number: str
    business_name: str
    status: str
    submitted_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)