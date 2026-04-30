# app/schemas/program.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .rule import LenderProgramRuleResponse


class LenderProgramCreate(BaseModel):
    """Create a new program under a lender."""
    lender_id: int
    name: str = Field(..., example="Tier 1")
    description: Optional[str] = None
    min_loan_amount: Optional[int] = None
    max_loan_amount: Optional[int] = None
    typical_term_months: Optional[int] = 60


class LenderProgramUpdate(BaseModel):
    """Update an existing program."""
    name: Optional[str] = None
    description: Optional[str] = None
    min_loan_amount: Optional[int] = None
    max_loan_amount: Optional[int] = None
    typical_term_months: Optional[int] = None


class LenderProgramResponse(BaseModel):
    """Response for lender program."""
    id: int
    lender_id: int
    name: str
    description: Optional[str] = None
    min_loan_amount: Optional[int] = None
    max_loan_amount: Optional[int] = None
    typical_term_months: Optional[int] = None
    rules: List[LenderProgramRuleResponse] = []

    model_config = ConfigDict(from_attributes=True)