from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.lender import Lender, LenderProgram, LenderProgramRule
from app.schemas.rule import (
    LenderProgramRuleCreate,
    LenderProgramRuleUpdate,
    LenderProgramRuleResponse
)

router = APIRouter(prefix="/rules", tags=["Lender Rules"])

@router.get("/rules/{program_id}", response_model=List[LenderProgramRuleResponse])
def get_rules_by_program(program_id: int, db: Session = Depends(get_db)):
    """
    Get all rules for a specific lender program.
    """
    rules = db.execute(
        select(LenderProgramRule)
        .where(LenderProgramRule.program_id == program_id)
        .order_by(LenderProgramRule.priority)
    ).scalars().all()
    
    if not rules:
        raise HTTPException(status_code=404, detail="No rules found for this program")

    return [
        LenderProgramRuleResponse.model_validate(rule)
        for rule in rules
    ]


@router.post("/rules", response_model=LenderProgramRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_in: LenderProgramRuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new rule for a specific lender program.
    """
    # Create new rule
    new_rule = LenderProgramRule(**rule_in.model_dump())
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return LenderProgramRuleResponse.model_validate(new_rule)

@router.put("/rules/{rule_id}", response_model=LenderProgramRuleResponse)
def update_rule(
    rule_id: int,
    rule_in: LenderProgramRuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing rule.
    """
    rule = db.execute(select(LenderProgramRule).where(LenderProgramRule.id == rule_id)).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update only the fields that were provided
    for key, value in rule_in.model_dump(exclude_unset=True).items():
        if key != "id" and hasattr(rule, key):
            setattr(rule, key, value)
            
    db.commit()
    db.refresh(rule)
    return LenderProgramRuleResponse.model_validate(rule)

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a rule by ID.
    This completes the CRUD operations for policy management.
    """
    rule = db.execute(select(LenderProgramRule).where(LenderProgramRule.id == rule_id)).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return None # 204 No Content
    
    
