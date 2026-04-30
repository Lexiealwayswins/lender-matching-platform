from app.models.match import ApplicationMatch, MatchRuleResult
from app.models.lender import LenderProgram

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List, Dict, Any

from app.database import get_db
from app.models.application import LoanApplication
from app.models.lender import Lender
from app.schemas.match import ApplicationMatchResponse, MatchRuleResultResponse

from app.workflows.underwriting_workflow import underwriting_workflow, hatchet

router = APIRouter(prefix="/match", tags=["Loan Application Matching"])

@router.post("/{application_id}/underwrite", status_code=status.HTTP_202_ACCEPTED)
async def run_underwriting(
    application_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger the asynchronous Hatchet workflow for underwriting.
    """
    application = db.execute(
        select(LoanApplication).where(LoanApplication.id == application_id)
    ).scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=404,
            detail=f"Application with id {application_id} not found"
        )

    if application.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="This application has already been underwritten"
        )

    # Create the context for workflow input
    workflow_input = {
        "application_id": application.id
    }
    
    workflow_run = underwriting_workflow.run_no_wait(
        {"application_id": application_id}
    )

    # Update application status
    application.status = "processing"
    db.commit()

    return {
        "status": "Processing", 
        "message": "Underwriting started in the background",
        "workflow_run_id": workflow_run.workflow_run_id
    }


@router.get("/{application_id}/matches", response_model=List[ApplicationMatchResponse])
def get_match_results(application_id: int, db: Session = Depends(get_db)):
    """
    Retrieve previous matching results for an application.
    Useful for viewing results again without re-running underwriting.
    """
    matches = db.execute(
        select(ApplicationMatch).where(ApplicationMatch.application_id == application_id)
    ).scalars().all()

    if not matches:
        raise HTTPException(status_code=404, detail="No match results found for this application")

    response = []
    for match in matches:
        result = db.execute(
            select(LenderProgram.name.label("p_name"), Lender.name.label("l_name"))
            .join(Lender, Lender.id == LenderProgram.lender_id)
            .where(LenderProgram.id == match.program_id)
        ).first()
        
        rule_results = db.execute(
            select(MatchRuleResult).where(MatchRuleResult.match_id == match.id)
        ).scalars().all()
        
        match_data = {
            "id": match.id,
            "program_id": match.program_id,
            "is_eligible": match.is_eligible,
            "fit_score": match.fit_score,
            "overall_reason": match.overall_reason,
            # injection result name
            "program_name": result.p_name if result else "Unknown",
            "lender_name": result.l_name if result else "Unknown",
            "rule_results": [
                MatchRuleResultResponse.model_validate(rule)
                for rule in rule_results
            ]
        }
        
        response.append(ApplicationMatchResponse(**match_data))

    return response