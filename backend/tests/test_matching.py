# backend/tests/test_matching.py
"""
Core business logic tests for the Lender Matching Platform.
Tests the MatchingService, RuleEvaluator, and overall matching accuracy.
"""

import pytest
from sqlalchemy.orm import Session
from app.services.rule_evaluator import RuleEvaluator
from app.services.matching_service import MatchingService
from app.models.application import LoanApplication
from app.models.lender import LenderProgramRule


def test_rule_evaluator_fico_pass(db: Session):
    """Test that a high FICO score passes the minimum FICO rule."""
    rule = db.query(LenderProgramRule).filter(
        LenderProgramRule.rule_type == "min_fico"
    ).first()

    application_data = {"fico_score": 750}
    passed, reason = RuleEvaluator.evaluate(rule, application_data)

    assert passed is True
    assert "passed" in reason.lower() or "Rule passed" in reason


def test_rule_evaluator_fico_fail(db: Session):
    """Test that a low FICO score fails and returns clear rejection reason."""
    rule = db.query(LenderProgramRule).filter(
        LenderProgramRule.rule_type == "min_fico"
    ).first()

    application_data = {"fico_score": 620}
    passed, reason = RuleEvaluator.evaluate(rule, application_data)

    assert passed is False
    assert "Minimum FICO required" in reason
    assert "620" in reason


def test_rule_evaluator_industry_exclusion(db: Session):
    """Test industry exclusion rule (e.g. Cannabis should be rejected)."""
    rule = db.query(LenderProgramRule).filter(
        LenderProgramRule.rule_type == "industry_exclusion"
    ).first()

    application_data = {"industry": "Cannabis"}
    passed, reason = RuleEvaluator.evaluate(rule, application_data)

    assert passed is False
    assert "not allowed" in reason.lower()


# ==================== Integration Tests ====================

def test_create_application(client):
    """Test that we can create a loan application via API."""
    response = client.post("/loans/", json={
        "business_name": "Test Engineering Corp",
        "industry": "Manufacturing",
        "state": "TX",
        "years_in_business": 5,
        "fico_score": 740,
        "paynet_score": 710,
        "has_bankruptcy": False,
        "requested_amount": 95000,
        "equipment_type": "CNC Machine",
        "equipment_age_years": 2
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "submitted"
    return data["id"]


def test_underwriting_flow(client):
    """Test the complete underwriting flow: create → match → validate results."""
    # Create application
    app_id = test_create_application(client)

    # Run underwriting
    response = client.post(f"/loans/{app_id}/underwrite")
    assert response.status_code == 200
    results = response.json()

    assert len(results) > 0, "Should return at least one lender match"
    
    # Check structure of results
    first_result = results[0]
    assert "lender_name" in first_result
    assert "fit_score" in first_result
    assert "is_eligible" in first_result
    assert "rule_results" in first_result
    assert len(first_result["rule_results"]) > 0, "Should have detailed rule results"


def test_fit_score_ranking(client):
    """Test that results are ranked by fit score (highest first)."""
    app_id = test_create_application(client)
    response = client.post(f"/loans/{app_id}/underwrite")
    results = response.json()

    scores = [r["fit_score"] for r in results]
    assert scores == sorted(scores, reverse=True), "Results should be sorted by fit score descending"


def test_match_rule_result_reason(client):
    """Test that rejection reasons are human-readable and informative."""
    app_id = test_create_application(client)
    response = client.post(f"/loans/{app_id}/underwrite")
    results = response.json()

    for match in results:
        for rule in match["rule_results"]:
            assert isinstance(rule["reason"], str)
            assert len(rule["reason"]) > 5, "Reason should be descriptive"
            assert rule["passed"] in [True, False]