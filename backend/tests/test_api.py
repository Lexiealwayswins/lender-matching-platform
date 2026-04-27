# backend/tests/test_api.py
"""
Comprehensive API tests for the Lender Matching Platform.

Tests:
- Loan Application CRUD
- Traditional underwriting
- Hatchet workflow (with proper mocking)
- Lender Policy endpoints
- Error handling
"""

import pytest
from unittest.mock import patch
from datetime import datetime


# ====================== Loan Application Tests ======================

def test_create_loan_application_success(client):
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
    return data["id"]


def test_create_application_validation_error(client):
    """Test that missing required fields returns 422 validation error."""
    payload = {"business_name": "Incomplete Corp"}
    response = client.post("/loans/", json=payload)
    assert response.status_code == 422


# ====================== Underwriting Tests ======================

def test_traditional_underwriting(client):
    """Test the traditional underwriting endpoint."""
    app_id = test_create_loan_application_success(client)

    response = client.post(f"/loans/{app_id}/underwrite")
    assert response.status_code == 200
    results = response.json()

    assert isinstance(results, list)
    assert len(results) > 0, "Should return matches from seeded lenders"

    first_match = results[0]
    assert "lender_name" in first_match
    assert "program_name" in first_match
    assert "is_eligible" in first_match
    assert "fit_score" in first_match
    assert 0 <= first_match["fit_score"] <= 100
    assert "rule_results" in first_match
    assert len(first_match["rule_results"]) > 0


def test_get_match_results(client):
    """Test retrieving previous match results."""
    app_id = test_create_loan_application_success(client)
    client.post(f"/loans/{app_id}/underwrite")

    response = client.get(f"/loans/{app_id}/matches")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0


# ====================== Hatchet Workflow Tests ======================

@patch("app.workflows.underwriting_workflow.hatchet.run_workflow")
def test_hatchet_underwriting_endpoint(mock_run_workflow, client):
    """
    Test the Hatchet workflow endpoint with proper mocking.
    This avoids requiring real Hatchet credentials during testing.
    """
    app_id = test_create_loan_application_success(client)

    response = client.post(f"/loans/{app_id}/underwrite-hatchet")
    assert response.status_code == 200
    data = response.json()

    assert data["application_id"] == app_id
    assert data["status"] == "workflow_queued"
    mock_run_workflow.assert_called_once()


# ====================== Lender Policy Tests ======================

def test_get_all_policies(client):
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


# ====================== Error Handling Tests ======================

def test_application_not_found(client):
    """Test 404 error when application does not exist."""
    response = client.post("/loans/99999/underwrite")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()