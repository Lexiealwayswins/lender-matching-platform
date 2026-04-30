from sqlalchemy import String, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Any, List
from .base import Base
from datetime import datetime


class Lender(Base):
    """Represents a financing company (e.g. Citizens Bank, Falcon Equipment Finance)."""
    __tablename__ = "lenders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    programs: Mapped[list["LenderProgram"]] = relationship(back_populates="lender")


class LenderProgram(Base):
    """
    A specific tier or program under a lender.
    Examples: Tier 1 / Tier 2 / Tier 3 from Stearns Bank [5], 
    Medical Program from Apex [4], or Standard Program from Falcon [2].
    """
    __tablename__ = "lender_programs"

    id: Mapped[int] = mapped_column(primary_key=True)
    lender_id: Mapped[int] = mapped_column(ForeignKey("lenders.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool | None] = mapped_column(default=True)
    min_loan_amount: Mapped[int | None] = mapped_column()
    max_loan_amount: Mapped[int | None] = mapped_column()
    typical_term_months: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    lender: Mapped["Lender"] = relationship(back_populates="programs")
    rules: Mapped[list["LenderProgramRule"]] = relationship(back_populates="program")


class LenderProgramRule(Base):
    """
    Core extensible rule table.
    This stores all rules parsed from the 5 PDFs (FICO, PayNet, TIB, 
    industry exclusions [5], bankruptcy years [2][3][5], state restrictions [1], etc.).
    Using rule_type + operator + value allows adding new rules from future PDFs 
    without changing the database schema.
    """
    __tablename__ = "lender_program_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("lender_programs.id"))
    
    rule_type: Mapped[str] = mapped_column(String(50))                      # maps to RuleType enum
    operator: Mapped[str] = mapped_column(String(20))                       # "gte", "lte", "in", "not_in"
    value: Mapped[str | None] = mapped_column(String(255))
    value_json: Mapped[Any | None] = mapped_column(JSON)                    # for lists (e.g. excluded industries [5])
    priority: Mapped[int | None] = mapped_column(default=100)
    failure_reason_template: Mapped[str | None] = mapped_column(Text)       # e.g. "Minimum FICO required is {threshold}, applicant has {actual}"
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    program: Mapped["LenderProgram"] = relationship(back_populates="rules")