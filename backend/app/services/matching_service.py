from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.application import LoanApplication
from app.models.lender import LenderProgram
from app.models.match import ApplicationMatch, MatchRuleResult
from app.services.rule_evaluator import RuleEvaluator


class MatchingService:
    """
    Core matching engine for the Lender Matching Platform.
    
    This service:
    1. Takes a loan application
    2. Evaluates it against all lender programs and their rules
    3. Generates detailed match results with clear rejection reasons
    4. Calculates a fit score (0-100) for ranking
    5. Persists results to the database
    
    This fulfills the main technical requirements:
    - Eligibility (yes/no)
    - Best matching program/tier
    - Specific reasons for rejection
    - Fit score for ranking
    """

    def __init__(self, db: Session):
        self.db = db

    def match_application(self, application: LoanApplication) -> List[ApplicationMatch]:
        """
        Main entry point: Match one loan application against all lenders.
        Returns a list of ApplicationMatch records (one per lender program).
        """
        application_data = self._prepare_application_data(application)
        matches = []

        # Get all active lender programs with their rules
        stmt = (
            select(LenderProgram)
            .join(LenderProgram.rules)
            .where(LenderProgram.is_active == True)
        )
        
        programs = self.db.scalars(stmt).unique().all()

        for program in programs:
            match_result = self._evaluate_program(program, application_data, application.id)
            matches.append(match_result)

        self.db.commit()
        return matches

    def _prepare_application_data(self, application: LoanApplication) -> Dict[str, Any]:
        """Convert LoanApplication object into a flat dict for easy rule evaluation."""
        return {
            # Borrower / Business Info
            "business_name": application.business_name,
            "industry": application.industry,
            "state": application.state,
            "years_in_business": application.years_in_business,
            "annual_revenue": application.annual_revenue,

            # Credit Info
            "fico_score": application.fico_score,
            "paynet_score": application.paynet_score,
            "has_bankruptcy": application.has_bankruptcy,
            "bankruptcy_years_ago": application.bankruptcy_years_ago,
            "has_judgements": application.has_judgements,
            "has_repossessions": application.has_repossessions,
            "highest_previous_debt": application.highest_previous_debt,

            # Loan Request
            "requested_amount": application.requested_amount,
            "requested_term_months": application.requested_term_months,
            "equipment_type": application.equipment_type,
            "equipment_age_years": application.equipment_age_years,
            "equipment_mileage": application.equipment_mileage,

            # Metadata
            "status": application.status,
            "submitted_at": application.submitted_at,
            "created_at": application.created_at,
            "updated_at": application.updated_at,
        }


    def _evaluate_program(
        self, 
        program: LenderProgram, 
        application_data: Dict[str, Any],
        application_id: int
    ) -> ApplicationMatch:
        """
        Evaluate a single LenderProgram against the application.
        Creates both ApplicationMatch and all MatchRuleResult records.
        """
        rule_results = []
        passed_count = 0
        total_rules = len(program.rules)

        for rule in sorted(program.rules, key=lambda r: r.priority):
            passed, reason = RuleEvaluator.evaluate(rule, application_data)
            
            if passed:
                passed_count += 1

            # Create detailed rule result instance (this is what UI will display)
            rule_result = MatchRuleResult(
                rule_id=rule.id,
                rule_type=rule.rule_type,
                passed=passed,
                actual_value=str(application_data.get(rule.rule_type, "N/A")),
                expected_value=rule.value or str(rule.value_json),
                reason=reason
            )
            rule_results.append(rule_result)

        # Calculate overall eligibility and fit score
        is_eligible = passed_count == total_rules
        fit_score = self._calculate_fit_score(passed_count, total_rules, program)

        overall_reason = "All criteria met" if is_eligible else "One or more criteria not met"

        # Create main match record instance
        match = ApplicationMatch(
            application_id=application_id,
            program_id=program.id,
            is_eligible=is_eligible,
            fit_score=fit_score,
            best_tier=program.name,
            overall_reason=overall_reason,
            created_at=datetime.now(timezone.utc)
        )

        self.db.add(match)
        self.db.flush()  # Get match.id

        # Link rule results to this match
        for rule_result in rule_results:
            rule_result.match_id = match.id
            self.db.add(rule_result)

        return match

    def _calculate_fit_score(self, passed_count: int, total_rules: int, program: LenderProgram) -> int:
        """
        Calculate a score from 0 to 100 based on how many rules passed.
        You can enhance this logic later (e.g. weight by rule priority).
        """
        if total_rules == 0:
            return 0
        base_score = int((passed_count / total_rules) * 100)
        
        # Bonus for higher tier programs (optional enhancement)
        if "Tier 1" in program.name:
            base_score = min(100, base_score + 5)
            
        return base_score
      