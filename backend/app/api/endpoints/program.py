# app/api/endpoints/program.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.lender import LenderProgram, LenderProgramRule
from app.schemas.program import (
    LenderProgramCreate,
    LenderProgramUpdate,
    LenderProgramResponse
)
from app.schemas.rule import LenderProgramRuleResponse

from app.workers.hatchet_worker import crud_workflow, hatchet

router = APIRouter(prefix="/programs", tags=["Lender Programs"])

@router.get("/{program_id}", response_model=LenderProgramResponse)
def get_program_by_id(program_id: int, db: Session = Depends(get_db)):
    """Get a single program by ID."""
    program = db.execute(
        select(LenderProgram).where(LenderProgram.id == program_id)
    ).scalar_one_or_none()

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    rules = db.execute(
        select(LenderProgramRule).where(LenderProgramRule.program_id == program.id)
    ).scalars().all()

    # ORM → Pydantic
    program_data = LenderProgramResponse.model_validate(program).model_dump()

    # inject rules（Pydantic）
    program_data["rules"] = [
        LenderProgramRuleResponse.model_validate(rule)
        for rule in rules
    ]
    
    return LenderProgramResponse(**program_data)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_program(
    program_in: LenderProgramCreate,
    db: Session = Depends(get_db)
):
    """Create a new program."""
    new_program = LenderProgram(**program_in.model_dump())
    db.add(new_program)
    db.commit()
    db.refresh(new_program)
    return LenderProgramResponse.model_validate(new_program)


@router.put("/{program_id}", response_model=LenderProgramResponse)
def update_program(
    program_id: int,
    program_in: LenderProgramUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing program."""
    program = db.execute(
        select(LenderProgram).where(LenderProgram.id == program_id)
    ).scalar_one_or_none()

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    for key, value in program_in.model_dump(exclude_unset=True).items():
        setattr(program, key, value)

    db.commit()
    db.refresh(program)
    return LenderProgramResponse.model_validate(program)


@router.delete("/{program_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_program(
    program_id: int,
    db: Session = Depends(get_db)
):
    """Delete a program and all its rules (cascade delete via Hatchet)."""
    crud_workflow.run_no_wait({
        "operation": "delete",
        "entity_type": "program",
        "data": {"id": program_id}
    })

    return None