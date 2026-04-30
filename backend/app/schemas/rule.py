# app/schemas/rule.py
"""
Pydantic schemas for lender policy rules management.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional
from datetime import datetime


class LenderProgramRuleBase(BaseModel):
    """Base schema for LenderProgramRule."""
    program_id: int = Field(..., description="Which program this rule belongs to")
    rule_type: str = Field(..., description="e.g. min_fico, industry_exclusion, bankruptcy_years")
    operator: str = Field(..., description="gte, lte, not_in, etc.")
    value: Optional[str] = Field(None, description="Main threshold value")
    value_json: Optional[Any] = Field(None, description="For list values like excluded industries")
    priority: int = Field(100, description="Lower number = higher priority")
    failure_reason_template: str = Field(..., description="Template for generating rejection reason")


class LenderProgramRuleCreate(LenderProgramRuleBase):
    """Schema used when creating a new rule."""
    model_config = ConfigDict(from_attributes=True)


class LenderProgramRuleUpdate(BaseModel):
    """Schema used when updating an existing rule."""
    rule_type: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None
    value_json: Optional[Any] = None
    priority: Optional[int] = None
    failure_reason_template: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LenderProgramRuleResponse(LenderProgramRuleBase):
    """Response schema when returning a rule."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)