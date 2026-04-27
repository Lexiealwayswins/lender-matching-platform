# backend/tests/test_api.py
"""
Clean API tests for the Lender Matching Platform.

This version:
- Removes all Hatchet related tests
- Uses unique application_number to avoid duplicate key errors
- Cleans database before each test
- Focuses on core functionality: application creation, underwriting, policies, and error handling
"""

import pytest
from datetime import datetime
import uuid
from app.models.match import MatchRuleResult, ApplicationMatch
from app.models.application import LoanApplication


def generate_unique_app_number():
    """Generate unique application number to prevent UniqueViolation errors."""
    return f"APP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"


# ====================== Loan Application Tests ======================

def test_create_loan_application_success(client, db):
    """Test successful creation of a loan application via POST /loans/."""
    # Clean previous test data
    db.query(MatchRuleResult).delete()
    db.query(ApplicationMatch).delete()
    db.query(LoanApplication).delete()
    db.commit()

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


def test_create_application_validation_error(client):
    """Test that missing required fields returns 422 validation error."""
    payload = {"business_name": "Incomplete Corp"}
    response = client.post("/loans/", json=payload)
    assert response.status_code == 422


# ====================== Underwriting Tests ======================

def test_traditional_underwriting(client, db):
    """Test the traditional underwriting endpoint (POST /loans/{id}/underwrite)."""
    db.query(MatchRuleResult).delete()
    db.query(ApplicationMatch).delete()
    db.query(LoanApplication).delete()
    db.commit()

    payload = {
        "business_name": "Test Corp",
        "industry": "Manufacturing",
        "state": "TX",
        "years_in_business": 5,
        "fico_score": 740,
        "requested_amount": 95000,
        "equipment_type": "Excavator"
    }

    create_response = client.post("/loans/", json=payload)
    app_id = create_response.json()["id"]

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


def test_get_match_results(client, db):
    """Test retrieving previous match results via GET /loans/{id}/matches."""
    db.query(MatchRuleResult).delete()
    db.query(ApplicationMatch).delete()
    db.query(LoanApplication).delete()
    db.commit()

    payload = {
        "business_name": "Test Corp",
        "industry": "Manufacturing",
        "state": "TX",
        "years_in_business": 5,
        "fico_score": 740,
        "requested_amount": 95000,
        "equipment_type": "Excavator"
    }

    create_response = client.post("/loans/", json=payload)
    app_id = create_response.json()["id"]
    client.post(f"/loans/{app_id}/underwrite")

    response = client.get(f"/loans/{app_id}/matches")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0


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
    """Test 404 error when trying to underwrite non-existent application."""
    response = client.post("/loans/99999/underwrite")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()