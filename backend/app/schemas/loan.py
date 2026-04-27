from pydantic import BaseModel, Field
from typing import Optional, List
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
    
    requested_amount: int = Field(..., gt=0, example=75000)
    requested_term_months: Optional[int] = Field(60, example=48)
    equipment_type: str = Field(..., example="Excavator")
    equipment_age_years: Optional[int] = Field(None, example=2)
    equipment_mileage: Optional[int] = Field(None, example=1200)

    class Config:
        schema_extra = {
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


class LoanApplicationResponse(BaseModel):
    """Response schema for loan application."""
    id: int
    application_number: str
    business_name: str
    status: str
    submitted_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MatchRuleResultResponse(BaseModel):
    """Detailed rule-by-rule matching result (for UI display)."""
    rule_type: str
    passed: bool
    actual_value: str
    expected_value: str
    reason: str

    class Config:
        from_attributes = True


class ApplicationMatchResponse(BaseModel):
    """Response for matching result of one lender program."""
    id: int
    program_id: int
    lender_name: str
    program_name: str
    is_eligible: bool
    fit_score: int
    overall_reason: str
    rule_results: List[MatchRuleResultResponse]

    class Config:
        from_attributes = True