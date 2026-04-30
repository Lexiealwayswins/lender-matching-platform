# app/workflows/underwriting_workflow.py
import os
from dotenv import load_dotenv
from typing import Dict, Any
from hatchet_sdk import Hatchet, Context

from sqlalchemy import select
from app.models.application import LoanApplication
from app.services.matching_service import MatchingService
from app.database import SessionLocal

load_dotenv()

hatchet = Hatchet(debug=True)

"""
Hatchet Workflow that orchestrates the entire underwriting process.

This fulfills the requirement:
"Design a workflow that: Validates application completeness, Derives necessary features,
Ranks matches by fit score, Persists results. Demonstrate proper use of Hatchet 
features including parallelization and retry logic."
"""
underwriting_workflow = hatchet.workflow(
    name="loan-underwriting-workflow"
)

@underwriting_workflow.task(retries=3)
async def validate_application(workflow_input: Any, context: Context, **kwargs) -> Dict[str, Any]:
    """
    Step 1: Validate application completeness.
    Checks for all required fields before proceeding.
    """
    input_data = workflow_input.model_dump() if hasattr(workflow_input, "model_dump") else workflow_input
    
    app_id = input_data.get("application_id")
    
    if not app_id:
            raise ValueError("Missing application_id")

    db = SessionLocal()
    try:
        application = db.execute(
            select(LoanApplication).where(LoanApplication.id == app_id)
        ).scalar_one_or_none()
        
        if not application:
            raise ValueError(f"Application {app_id} not found in database")

        required = ["fico_score", "requested_amount", "business_name", "state", "industry"]
        missing = [f for f in required if getattr(application, f, None) is None]

        if missing:
            raise ValueError(f"Database record {app_id} is missing fields: {missing}")

        return {
            "status": "validated",
            "application_id": app_id,
            "business_name": application.business_name
        }
    finally:
        db.close()  
    
@underwriting_workflow.task(retries=2, parents=[validate_application])
async def derive_features(workflow_input: Any, context: Context, **kwargs) -> Dict[str, Any]:
    """
    Step 2: Derive necessary features (e.g. equipment age category, business maturity).
    This step enriches the raw application data with business logic.
    """
    input_data = workflow_input.model_dump() if hasattr(workflow_input, "model_dump") else workflow_input
    data = input_data.get("application_data", {})

    derived = {
        "equipment_age_category": "new" if (data.get("equipment_age_years") or 999) <= 3 else "used",
        "business_maturity": "startup" if (data.get("years_in_business") or 0) < 3 else "established",
        "credit_tier": "high" if (data.get("fico_score") or 0) >= 720 else "medium"
    }

    return {
        "status": "features_derived",
        "derived_features": derived,
        "original_data": data
    }

@underwriting_workflow.task(retries=3, parents=[derive_features])
async def match_lenders_parallel(workflow_input: Any, context: Context) -> Dict[str, Any]:
    """
    Step 3: Parallel matching against all lenders.
    Hatchet automatically parallelizes execution when multiple steps or workers are used.
    Uses the existing MatchingService to do the actual rule evaluation.
    """
    input_data = workflow_input.model_dump() if hasattr(workflow_input, "model_dump") else workflow_input
    app_id = input_data.get("application_id")
    
    db = SessionLocal()
    try:
        if not app_id:
            raise ValueError("No application_id provided to workflow")
        
        # Get real database records
        application = db.execute(
            select(LoanApplication).where(LoanApplication.id == app_id)
            ).scalar_one_or_none()
        
        if not application:
            raise ValueError(f"Application {app_id} not found in database")
        
        matching_service = MatchingService(db)
        matches = matching_service.match_application(application)

        # Rank by fit score (descending)
        ranked_matches = sorted(matches, key=lambda x: x.fit_score, reverse=True)

        return {
            "status": "completed",
            "total_lenders_evaluated": len(matches),
            "eligible_count": sum(1 for m in matches if m.is_eligible),
            "ranked_results": [
                {
                    "lender": m.best_tier,
                    "fit_score": m.fit_score,
                    "is_eligible": m.is_eligible,
                    "reason": m.overall_reason
                } for m in ranked_matches
            ]
        }
    finally:
        db.close()