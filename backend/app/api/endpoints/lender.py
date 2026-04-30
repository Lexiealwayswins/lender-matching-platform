# app/api/endpoints/lender.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.lender import Lender, LenderProgram, LenderProgramRule
from app.schemas.lender import (
    LenderCreate,
    LenderUpdate,
    LenderResponse,
    LenderWithProgramsResponse
)

from app.schemas.program import LenderProgramResponse
from app.schemas.rule import LenderProgramRuleResponse

from app.workers.hatchet_worker import crud_workflow, hatchet

router = APIRouter(prefix="/lenders", tags=["Lenders"])


@router.get("/", response_model=List[LenderWithProgramsResponse])
def get_all_lenders(db: Session = Depends(get_db)):
    """
    Return all lenders with their programs and rules.
    This endpoint is used by the frontend 'Lender Policy Screen'.
    """
    lenders = db.execute(select(Lender)).scalars().all()
    result = []

    for lender in lenders:
        programs = db.execute(
            select(LenderProgram).where(LenderProgram.lender_id == lender.id)
        ).scalars().all()

        program_list = []
        for program in programs:
            rules = db.execute(
                select(LenderProgramRule).where(LenderProgramRule.program_id == program.id)
            ).scalars().all()

            program_data = LenderProgramResponse.model_validate(program).model_dump()

            program_data["rules"] = [
                LenderProgramRuleResponse.model_validate(rule)
                for rule in rules
            ]

            program_list.append(LenderProgramResponse(**program_data))

        lender_data = LenderWithProgramsResponse.model_validate(lender).model_dump()
        lender_data["programs"] = program_list

        result.append(LenderWithProgramsResponse(**lender_data))

    return result


@router.get("/{lender_id}", response_model=LenderWithProgramsResponse)
def get_lender_by_id(lender_id: int, db: Session = Depends(get_db)):
    """Get a single lender with all its programs and rules."""
    lender = db.execute(
        select(Lender).where(Lender.id == lender_id)
    ).scalar_one_or_none()

    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")

    programs = db.execute(
        select(LenderProgram).where(LenderProgram.lender_id == lender.id)
    ).scalars().all()

    program_list = []
    for program in programs:
        rules = db.execute(
            select(LenderProgramRule).where(LenderProgramRule.program_id == program.id)
        ).scalars().all()
        
        program_data = LenderProgramResponse.model_validate(program).model_dump()

        program_data["rules"] = [
            LenderProgramRuleResponse.model_validate(rule)
            for rule in rules
        ]

    lender_data = LenderWithProgramsResponse.model_validate(lender).model_dump()
    lender_data["programs"] = program_list

    return  LenderWithProgramsResponse(**lender_data)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_lender(
    lender_in: LenderCreate,
    db: Session = Depends(get_db)
):
    """Create a new lender."""
    new_lender = Lender(**lender_in.model_dump())
    db.add(new_lender)
    db.commit()
    db.refresh(new_lender)
    return LenderResponse.model_validate(new_lender)


@router.put("/{lender_id}", response_model=dict)
def update_lender(
    lender_id: int,
    lender_in: LenderUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing lender."""
    lender = db.execute(
        select(Lender).where(Lender.id == lender_id)
    ).scalar_one_or_none()

    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")

    for key, value in lender_in.model_dump(exclude_unset=True).items():
        setattr(lender, key, value)

    db.commit()
    db.refresh(lender)
    return LenderResponse.model_validate(lender)


@router.delete("/{lender_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_lender(
    lender_id: int,
    db: Session = Depends(get_db)
):
    """Delete a lender and all its programs + rules (cascade delete via Hatchet)."""
    crud_workflow.run_no_wait({
        "operation": "delete",
        "entity_type": "lender",
        "data": {"id": lender_id}
    })
    return None