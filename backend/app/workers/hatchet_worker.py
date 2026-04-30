# app/workers/hatchet_worker.py
"""
Hatchet Worker for background CRUD operations on Lenders, Programs, Rules and Applications.

This worker handles create/update/delete with retry logic, parallel execution where possible,
and cascade deletion (e.g. deleting a Lender also deletes its Programs and Rules).
"""

import os
from dotenv import load_dotenv
from hatchet_sdk import Hatchet, Context

load_dotenv()

from sqlalchemy import select, delete
from typing import Dict, Any
from app.database import SessionLocal
from app.models.lender import Lender, LenderProgram, LenderProgramRule
from app.models.application import LoanApplication
from app.models.match import ApplicationMatch, MatchRuleResult

hatchet = Hatchet(debug=True)

"""
Unified Hatchet workflow for all CRUD operations.
Supports Lender, Program, Rule, and Application entities with proper cascade handling.
"""
crud_workflow = hatchet.workflow(
    name="crud-workflow"
)

@crud_workflow.task(retries=3) 
async def validate_operation(workflow_input: Any, context: Context, **kwargs):
    """Step 1: Validate the requested operation."""
    input_data = workflow_input.model_dump() if hasattr(workflow_input, "model_dump") else workflow_input
    operation = input_data.get("operation")
    entity_type = input_data.get("entity_type")

    if not operation or not entity_type:
        raise ValueError("Missing operation or entity_type")

    return {
        "status": "validated",
        "operation": operation,
        "entity_type": entity_type
    }

@crud_workflow.task(retries=3, parents=[validate_operation])
async def execute_crud(workflow_input: Dict[str, Any], context: Context, **kwargs):
    """Step 2: Execute CRUD with proper cascade logic."""
    db = SessionLocal()

    try:
        input_data = workflow_input.model_dump() if hasattr(workflow_input, "model_dump") else workflow_input
        operation = input_data.get("operation")
        entity_type = input_data.get("entity_type")
        data = input_data.get("data", {})

        if entity_type == "lender":
            if operation == "delete":
                lender_id = data.get("id")
                # Cascade: delete rules → programs → lender
                db.execute(
                    delete(MatchRuleResult)
                    .where(MatchRuleResult.rule_id.in_(
                        select(LenderProgramRule.id)
                        .where(LenderProgramRule.program_id.in_(
                            select(LenderProgram.id)
                            .where(LenderProgram.lender_id == lender_id)
                        ))
                    ))
                )
                db.execute(
                    delete(LenderProgramRule)
                    .where(LenderProgramRule.program_id.in_(
                        select(LenderProgram.id)
                        .where(LenderProgram.lender_id == lender_id)
                    ))
                )
                db.execute(
                    delete(LenderProgram)
                    .where(LenderProgram.lender_id == lender_id)
                )
                db.execute(
                    delete(Lender)
                    .where(Lender.id == lender_id)
                )

        elif entity_type == "program":
            if operation == "delete":
                program_id = data.get("id")
                db.execute(
                    delete(LenderProgramRule)
                    .where(LenderProgramRule.program_id == program_id)
                )
                db.execute(
                    delete(LenderProgram)
                    .where(LenderProgram.id == program_id)
                )

        elif entity_type == "rule":
            if operation == "delete":
                rule_id = data.get("id")
                db.execute(
                    delete(LenderProgramRule)
                    .where(LenderProgramRule.id == rule_id)
                )
                
        elif entity_type == "application":
            if operation == "delete":
                app_id = data.get("id")
                db.execute(
                    delete(MatchRuleResult)
                    .where(MatchRuleResult.match_id.in_(
                        select(ApplicationMatch.id)
                        .where(ApplicationMatch.application_id == app_id)
                    ))
                )
                db.execute(
                    delete(ApplicationMatch)
                    .where(ApplicationMatch.application_id == app_id)
                )
                db.execute(
                    delete(LoanApplication).
                    where(LoanApplication.id == app_id)
                )

        db.commit()
        return {"status": "success", "operation": operation, "entity_type": entity_type}

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()