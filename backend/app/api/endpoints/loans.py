from datetime import datetime
from app.models.match import ApplicationMatch, MatchRuleResult
from app.models.lender import LenderProgram

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.config import settings
from app.database import get_db
from app.models.application import LoanApplication
from app.models.lender import Lender
from app.services.matching_service import MatchingService
from app.schemas.loan import (
    LoanApplicationCreate,
    LoanApplicationResponse,
    ApplicationMatchResponse
)

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/", response_model=LoanApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_loan_application(
    application_in: LoanApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new loan application.
    This is the entry point for brokers to submit applications.
    """
    # Generate a unique application number
    application_number = f"APP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    application = LoanApplication(
        application_number=application_number,
        business_name=application_in.business_name,
        industry=application_in.industry,
        state=application_in.state,
        years_in_business=application_in.years_in_business,
        annual_revenue=application_in.annual_revenue,
        fico_score=application_in.fico_score,
        paynet_score=application_in.paynet_score,
        has_bankruptcy=application_in.has_bankruptcy,
        bankruptcy_years_ago=application_in.bankruptcy_years_ago,
        requested_amount=application_in.requested_amount,
        requested_term_months=application_in.requested_term_months,
        equipment_type=application_in.equipment_type,
        equipment_age_years=application_in.equipment_age_years,
        equipment_mileage=application_in.equipment_mileage,
        status="submitted",
        submitted_at=datetime.utcnow()
    )

    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.post("/{application_id}/underwrite", response_model=List[ApplicationMatchResponse])
def run_underwriting(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Run the matching engine against all lenders.
    This triggers the core MatchingService and returns detailed results.
    """
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    
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

    # Run matching engine
    matching_service = MatchingService(db)
    matches = matching_service.match_application(application)

    # Update application status
    application.status = "completed"
    db.commit()

    # Enhance response with lender names
    response = []
    for match in matches:
        program = db.query(LenderProgram).filter(LenderProgram.id == match.program_id).first()
        lender = db.query(Lender).filter(Lender.id == program.lender_id).first() if program else None

        # Get rule results for this match
        rule_results = db.query(MatchRuleResult).filter(
            MatchRuleResult.match_id == match.id
        ).all()

        response.append({
            "id": match.id,
            "program_id": match.program_id,
            "lender_name": lender.name if lender else "Unknown",
            "program_name": program.name if program else "Unknown",
            "is_eligible": match.is_eligible,
            "fit_score": match.fit_score,
            "overall_reason": match.overall_reason,
            "rule_results": rule_results
        })

    return response


@router.get("/{application_id}/matches", response_model=List[ApplicationMatchResponse])
def get_match_results(application_id: int, db: Session = Depends(get_db)):
    """
    Retrieve previous matching results for an application.
    Useful for viewing results again without re-running underwriting.
    """
    matches = db.query(ApplicationMatch).filter(
        ApplicationMatch.application_id == application_id
    ).all()

    if not matches:
        raise HTTPException(status_code=404, detail="No match results found for this application")

    # Similar enhancement as above...
    response = []
    for match in matches:
        program = db.query(LenderProgram).filter(LenderProgram.id == match.program_id).first()
        lender = db.query(Lender).filter(Lender.id == program.lender_id).first() if program else None
        rule_results = db.query(MatchRuleResult).filter(
            MatchRuleResult.match_id == match.id
        ).all()

        response.append({
            "id": match.id,
            "program_id": match.program_id,
            "lender_name": lender.name if lender else "Unknown",
            "program_name": program.name if program else "Unknown",
            "is_eligible": match.is_eligible,
            "fit_score": match.fit_score,
            "overall_reason": match.overall_reason,
            "rule_results": rule_results
        })

    return response