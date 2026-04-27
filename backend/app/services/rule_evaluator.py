from typing import Dict, Any, Tuple
from app.models.base import RuleType


class RuleEvaluator:
    """
    Evaluates individual rules against loan application data.
    This class handles all rule types extracted from the 5 lender PDFs.
    """

    @staticmethod
    def evaluate(rule: Any, application_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluate a single LenderProgramRule against the application.
        Returns (passed: bool, reason: str)
        """
        rule_type = rule.rule_type
        operator = rule.operator
        expected = rule.value
        expected_json = rule.value_json
        template = rule.failure_reason_template or "Rule {rule_type} failed"

        actual_value = application_data.get(rule_type)

        # Handle different rule types from the 5 PDFs
        if rule_type == RuleType.MIN_FICO.value:
            actual = application_data.get("fico_score")
            return RuleEvaluator._compare_numeric(actual, expected, operator, template)

        elif rule_type == RuleType.MIN_PAYNET.value:
            actual = application_data.get("paynet_score")
            return RuleEvaluator._compare_numeric(actual, expected, operator, template)

        elif rule_type == RuleType.MIN_TIME_IN_BUSINESS.value:
            actual = application_data.get("years_in_business")
            return RuleEvaluator._compare_numeric(actual, expected, operator, template)

        elif rule_type == RuleType.MAX_LOAN_AMOUNT.value or rule_type == RuleType.MIN_LOAN_AMOUNT.value:
            actual = application_data.get("requested_amount")
            return RuleEvaluator._compare_numeric(actual, expected, operator, template)

        elif rule_type == RuleType.BANKRUPTCY_YEARS.value:
            if not application_data.get("has_bankruptcy"):
                return True, "No bankruptcy history - rule passed"
            actual = application_data.get("bankruptcy_years_ago", 0)
            passed, reason = RuleEvaluator._compare_numeric(actual, expected, operator, template)
            return passed, reason if passed else f"Bankruptcy must be discharged at least {expected} years ago (currently {actual} years)"

        elif rule_type == RuleType.INDUSTRY_EXCLUSION.value:
            industry = application_data.get("industry")
            if industry in (expected_json or []):
                return False, template.format(actual=industry)
            return True, "Industry is allowed"

        elif rule_type == RuleType.STATE_RESTRICTION.value:
            state = application_data.get("state")
            if state in (expected_json or []):
                return False, template.format(actual=state)
            return True, "State is allowed"

        elif rule_type == RuleType.MAX_EQUIPMENT_AGE.value:
            actual = application_data.get("equipment_age_years")
            return RuleEvaluator._compare_numeric(actual, expected, operator, template)

        elif rule_type == RuleType.COMPARABLE_DEBT.value:
            # Simplified version - can be enhanced later
            return True, "Comparable debt check passed (placeholder)"
          
        # If there is a new PDF, here we can add more elif logics without updating database schema

        else:
            return True, f"Unknown rule type {rule_type} - skipped"
          

    @staticmethod
    def _compare_numeric(actual: Any, expected: Any, operator: str, template: str) -> Tuple[bool, str]:
        """Helper method to compare numeric values."""
        if actual is None:
            return False, "Missing required data for rule evaluation"

        try:
            actual_val = float(actual)
            expected_val = float(expected)
        except (TypeError, ValueError):
            return False, "Invalid numeric value for comparison"

        if operator == "gte":
            passed = actual_val >= expected_val
            reason = template.format(threshold=expected, actual=actual) if not passed else "Rule passed"
            return passed, reason
        elif operator == "lte":
            passed = actual_val <= expected_val
            reason = template.format(threshold=expected, actual=actual) if not passed else "Rule passed"
            return passed, reason

        return False, "Unsupported operator"