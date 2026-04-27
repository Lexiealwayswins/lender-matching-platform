from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.lender import Lender, LenderProgram, LenderProgramRule
from app.schemas.loan import LoanApplicationCreate  # Reuse some schemas if needed

router = APIRouter(prefix="/policies", tags=["Lender Policies"])


@router.get("/lenders", response_model=List[dict])
def get_all_lenders(db: Session = Depends(get_db)):
    """
    Return all lenders with their programs and rules.
    This endpoint is used by the frontend 'Lender Policy Screen'.
    """
    lenders = db.query(Lender).all()
    result = []

    for lender in lenders:
        programs = db.query(LenderProgram).filter(
            LenderProgram.lender_id == lender.id
        ).all()

        lender_data = {
            "id": lender.id,
            "name": lender.name,
            "description": lender.description,
            "programs": []
        }

        for program in programs:
            rules = db.query(LenderProgramRule).filter(
                LenderProgramRule.program_id == program.id
            ).order_by(LenderProgramRule.priority).all()

            program_data = {
                "id": program.id,
                "name": program.name,
                "description": program.description,
                "min_loan_amount": program.min_loan_amount,
                "max_loan_amount": program.max_loan_amount,
                "rules": [
                    {
                        "id": rule.id,
                        "rule_type": rule.rule_type,
                        "operator": rule.operator,
                        "value": rule.value,
                        "value_json": rule.value_json,
                        "priority": rule.priority,
                        "failure_reason_template": rule.failure_reason_template
                    } for rule in rules
                ]
            }
            lender_data["programs"].append(program_data)

        result.append(lender_data)

    return result


@router.get("/rules/{program_id}")
def get_rules_by_program(program_id: int, db: Session = Depends(get_db)):
    """
    Get all rules for a specific lender program.
    Useful for editing rules in the admin/policy management UI.
    """
    rules = db.query(LenderProgramRule).filter(
        LenderProgramRule.program_id == program_id
    ).order_by(LenderProgramRule.priority).all()

    if not rules:
        raise HTTPException(status_code=404, detail="Program not found or has no rules")

    return rules


@router.post("/rules")
def add_or_update_rule(
    rule_data: dict,
    db: Session = Depends(get_db)
):
    """
    Add a new rule or update an existing rule.
    This supports the requirement: "easy to edit existing criteria and easy to add more kinds of policy checks".
    
    Example rule_data:
    {
        "program_id": 1,
        "rule_type": "min_fico",
        "operator": "gte",
        "value": "720",
        "failure_reason_template": "Minimum FICO required is {threshold}, applicant has {actual}"
    }
    """
    # This is a simplified version. In production, you should use Pydantic models.
    if "id" in rule_data:  # Update existing rule
        rule = db.query(LenderProgramRule).filter(LenderProgramRule.id == rule_data["id"]).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        for key, value in rule_data.items():
            if key != "id" and hasattr(rule, key):
                setattr(rule, key, value)
    else:  # Create new rule
        new_rule = LenderProgramRule(**rule_data)
        db.add(new_rule)

    db.commit()
    return {"status": "success", "message": "Rule saved successfully"}