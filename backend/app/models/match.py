from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List
from .base import Base


class ApplicationMatch(Base):
    """
    Stores the result of running the matching engine against a LoanApplication.
    One record per LenderProgram. Contains overall eligibility, fit score,
    and links to detailed per-rule results.
    """
    __tablename__ = "application_matches"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("lender_programs.id"), nullable=False)
    
    is_eligible = Column(Boolean, nullable=False)
    fit_score = Column(Integer, default=0)                    # 0-100
    best_tier = Column(String(50))
    overall_reason = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())

    application = relationship("LoanApplication", back_populates="matches")
    rule_results: List["MatchRuleResult"] = relationship("MatchRuleResult", back_populates="match")


class MatchRuleResult(Base):
    """
    Detailed per-rule matching result.
    This fulfills the UI requirement to show exactly which criteria passed/failed
    and why (e.g. "Minimum FICO required is 725 [5], applicant has 680").
    """
    __tablename__ = "match_rule_results"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("application_matches.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("lender_program_rules.id"), nullable=False)
    
    rule_type = Column(String(50), nullable=False)
    passed = Column(Boolean, nullable=False)
    actual_value = Column(String(100))
    expected_value = Column(String(100))
    reason = Column(Text, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())

    match = relationship("ApplicationMatch", back_populates="rule_results")