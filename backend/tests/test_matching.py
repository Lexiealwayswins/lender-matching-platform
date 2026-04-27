# backend/tests/test_matching.py
"""
Core business logic tests for the Lender Matching Platform.
Tests RuleEvaluator, MatchingService, and matching accuracy.
"""

import pytest
from app.services.rule_evaluator import RuleEvaluator
from app.models.lender import LenderProgramRule


def test_rule_evaluator_fico_pass(db):
    """Test that a high FICO score passes the minimum FICO rule."""
    rule = db.query(LenderProgramRule).filter(
        LenderProgramRule.rule_type == "min_fico"
    ).first()

    application_data = {"fico_score": 750}
    passed, reason = RuleEvaluator.evaluate(rule, application_data)

    assert passed is True
    assert "passed" in reason.lower() or "Rule passed" in reason


def test_rule_evaluator_fico_fail(db):
    """Test that a low FICO score fails with clear rejection reason."""
    rule = db.query(LenderProgramRule).filter(
        LenderProgramRule.rule_type == "min_fico"
    ).first()

    application_data = {"fico_score": 620}
    passed, reason = RuleEvaluator.evaluate(rule, application_data)

    assert passed is False
    assert "Minimum FICO required" in reason
    assert "620" in reason


def test_rule_evaluator_industry_exclusion(db):
    """Test industry exclusion rule (e.g. Cannabis should be rejected)."""
    rule = db.query(LenderProgramRule).filter(
        LenderProgramRule.rule_type == "industry_exclusion"
    ).first()

    application_data = {"industry": "Cannabis"}
    passed, reason = RuleEvaluator.evaluate(rule, application_data)

    assert passed is False
    assert "not allowed" in reason.lower()