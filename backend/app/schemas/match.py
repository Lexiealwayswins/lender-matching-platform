# app/schemas/match.py
"""
Pydantic schemas for matching results.
These schemas are used for API responses to ensure clean JSON output to the frontend.
"""

from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Optional, Any


class MatchRuleResultResponse(BaseModel):
    """Detailed per-rule result shown in the frontend results page."""
    rule_type: str
    passed: bool
    actual_value: str
    expected_value: str
    reason: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationMatchResponse(BaseModel):
    """Response model for a single lender match result.
    
    This includes lender name, program name, fit score, eligibility,
    and the detailed list of rule results (what the UI displays).
    """
    id: int
    program_id: int
    lender_name: str
    program_name: str
    is_eligible: bool
    fit_score: int
    overall_reason: str
    rule_results: List[MatchRuleResultResponse]
    
    model_config = ConfigDict(from_attributes=True)
    
    @model_validator(mode='before')
    @classmethod
    def extract_names(cls, data: Any) -> Any:
        # if data is dict, return 
        if isinstance(data, dict):
            return data
            
        # if data is SQLAlchemy ORM object
        # we put data into Pydantic
        try:
            if hasattr(data, "program") and data.program:
                # get Program Name
                setattr(data, "program_name", data.program.name)
                
                # get Lender Name (from program -> lender)
                if hasattr(data.program, "lender") and data.program.lender:
                    setattr(data, "lender_name", data.program.lender.name)
                else:
                    setattr(data, "lender_name", "N/A")
            else:
                setattr(data, "program_name", "N/A")
                setattr(data, "lender_name", "N/A")
        except Exception:
            setattr(data, "program_name", "Unknown")
            setattr(data, "lender_name", "Unknown")
            
        return data


class MatchSummaryResponse(BaseModel):
    """Optional: Summary of matching results (can be used in future extensions)."""
    total_lenders: int
    eligible_count: int
    average_fit_score: float
    best_match: Optional[str] = None


# For internal use or future expansion
class MatchRequest(BaseModel):
    """If you want to accept custom matching parameters in the future."""
    application_id: int
    use_hatchet: bool = False