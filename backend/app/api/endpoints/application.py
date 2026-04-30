from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.application import LoanApplication
from app.schemas.application import (
    LoanApplicationCreate,
    LoanApplicationUpdate,
    LoanApplicationResponse,
)

from app.workers.hatchet_worker import crud_workflow, hatchet

router = APIRouter(prefix="/application", tags=["Loan Applications"])

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
    application_number = f"APP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    application = LoanApplication(
        application_number=application_number,
        status="submitted",
        **application_in.model_dump()
    )

    db.add(application)
    db.commit()
    db.refresh(application)
    return LoanApplicationResponse.model_validate(application)


@router.get("/", response_model=List[LoanApplicationResponse])
def get_all_applications(db: Session = Depends(get_db)):
    """Get all loan applications."""
    applications = db.execute(select(LoanApplication)).scalars().all()
    return [
        LoanApplicationResponse.model_validate(application)
        for application in applications
    ]


@router.get("/{application_id}", response_model=LoanApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """Get a single application by ID."""
    application = db.execute(
        select(LoanApplication).where(LoanApplication.id == application_id)
    ).scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return LoanApplicationResponse.model_validate(application)


@router.put("/{application_id}", response_model=LoanApplicationResponse)
def update_application(
    application_id: int,
    application_in: LoanApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing application."""
    application = db.execute(
        select(LoanApplication).where(LoanApplication.id == application_id)
    ).scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    for key, value in application_in.model_dump(exclude_unset=True).items():
        setattr(application, key, value)

    db.commit()
    db.refresh(application)
    return LoanApplicationResponse.model_validate(application)


@router.delete("/{application_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Trigger async deletion of an application and its match results (cascade)."""
    crud_workflow.run_no_wait({
        "operation": "delete",
        "entity_type": "application",
        "data": {"id": application_id}
    })

    return None