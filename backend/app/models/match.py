from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base
from typing import TYPE_CHECKING
from datetime import datetime

# To avoid pylance error
if TYPE_CHECKING:
    from .application import LoanApplication

class ApplicationMatch(Base):
    """
    Stores the result of running the matching engine against a LoanApplication.
    One record per LenderProgram. Contains overall eligibility, fit score,
    and links to detailed per-rule results.
    """
    __tablename__ = "application_matches"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("loan_applications.id"))
    program_id: Mapped[int] = mapped_column(ForeignKey("lender_programs.id"))
    
    is_eligible: Mapped[bool] = mapped_column()
    fit_score: Mapped[int | None] = mapped_column(default=0)  # 0-100
    best_tier: Mapped[str | None] = mapped_column(String(50))
    overall_reason: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    application: Mapped["LoanApplication"] = relationship(back_populates="matches")
    rule_results: Mapped[list["MatchRuleResult"]] = relationship(back_populates="match")


class MatchRuleResult(Base):
    """
    Detailed per-rule matching result.
    This fulfills the UI requirement to show exactly which criteria passed/failed
    and why (e.g. "Minimum FICO required is 725 [5], applicant has 680").
    """
    __tablename__ = "match_rule_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("application_matches.id"))
    rule_id: Mapped[int] = mapped_column(ForeignKey("lender_program_rules.id"))
    
    rule_type: Mapped[str] = mapped_column(String(50))
    passed: Mapped[bool] = mapped_column()
    actual_value: Mapped[str | None] = mapped_column(String(100))
    expected_value: Mapped[str | None] = mapped_column(String(100))
    reason: Mapped[str] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    match: Mapped["ApplicationMatch"] = relationship(back_populates="rule_results")