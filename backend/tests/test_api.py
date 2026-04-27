# backend/tests/test_api.py
"""
Comprehensive API tests for the Lender Matching Platform.

This file tests:
- Loan Application CRUD operations
- Traditional underwriting endpoint
- Hatchet workflow endpoint (with mocking)
- Lender Policy endpoints
- Error handling and validation
- Integration between API and MatchingService

All tests include detailed English comments for clarity.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


# ====================== Loan Application Tests ======================

def test_create_loan_application_success():
    """Test successful creation of a loan application via POST /loans/."""
    payload = {
        "business_name": "Acme Manufacturing Inc",
        "industry": "Manufacturing",
        "state": "TX",
        "years_in_business": 7,
        "annual_revenue": 2500000,
        "fico_score": 765,
        "paynet_score": 720,
        "has_bankruptcy": False,
        "requested_amount": 125000,
        "requested_term_months": 60,
        "equipment_type": "CNC Lathe",
        "equipment_age_years": 1
    }

    response = client.post("/loans/", json=payload)
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["business_name"] == "Acme Manufacturing Inc"
    assert data["status"] == "submitted"
    assert "application_number" in data
    return data["id"]  # Return ID for subsequent tests


def test_create_application_validation_error():
    """Test that missing required fields returns 422 validation error."""
    payload = {
        "business_name": "Incomplete Corp",
        # Missing required fields: industry, state, fico_score, requested_amount, equipment_type
    }
    response = client.post("/loans/", json=payload)
    assert response.status_code == 422


# ====================== Underwriting Tests ======================

def test_traditional_underwriting():
    """Test the traditional underwriting endpoint (POST /loans/{id}/underwrite)."""
    app_id = test_create_loan_application_success()

    response = client.post(f"/loans/{app_id}/underwrite")
    assert response.status_code == 200
    results = response.json()

    assert isinstance(results, list)
    assert len(results) > 0, "Should return matches from seeded lenders"

    # Check structure of each match result
    first_match = results[0]
    assert "lender_name" in first_match
    assert "program_name" in first_match
    assert "is_eligible" in first_match
    assert "fit_score" in first_match
    assert isinstance(first_match["fit_score"], int)
    assert 0 <= first_match["fit_score"] <= 100
    assert "rule_results" in first_match
    assert len(first_match["rule_results"]) > 0


def test_get_match_results():
    """Test retrieving previous match results via GET /loans/{id}/matches."""
    app_id = test_create_loan_application_success()
    client.post(f"/loans/{app_id}/underwrite")  # Ensure results exist

    response = client.get(f"/loans/{app_id}/matches")
    assert response.status_code == 200
    results = response.json()

    assert len(results) > 0
    assert all("rule_results" in match for match in results)


# ====================== Hatchet Workflow Tests ======================

@patch("app.workflows.underwriting_workflow.hatchet.run_workflow")
def test_hatchet_underwriting_endpoint(mock_run_workflow):
    """
    Test the Hatchet workflow endpoint.
    We mock the actual Hatchet call to avoid needing real credentials.
    """
    app_id = test_create_loan_application_success()

    response = client.post(f"/loans/{app_id}/underwrite-hatchet")
    assert response.status_code == 200
    data = response.json()

    assert data["application_id"] == app_id
    assert data["status"] == "workflow_queued"
    assert "note" in data

    # Verify that Hatchet run_workflow was called
    mock_run_workflow.assert_called_once()


# ====================== Lender Policy Tests ======================

def test_get_all_policies():
    """Test retrieving all lender policies and their rules."""
    response = client.get("/policies/lenders")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 5, "Should return at least 5 lenders from seed data"

    first_lender = data[0]
    assert "name" in first_lender
    assert "programs" in first_lender
    assert len(first_lender["programs"]) > 0


def test_get_rules_by_program():
    """Test retrieving rules for a specific lender program."""
    # Get first program (assume ID 1 from seed)
    response = client.get("/policies/rules/1")
    assert response.status_code in [200, 404]  # 404 is acceptable if ID doesn't exist

    if response.status_code == 200:
        rules = response.json()
        assert isinstance(rules, list)
        if len(rules) > 0:
            assert "rule_type" in rules[0]
            assert "operator" in rules[0]


# ====================== Error Handling Tests ======================

def test_application_not_found():
    """Test 404 error when trying to underwrite non-existent application."""
    response = client.post("/loans/99999/underwrite")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()