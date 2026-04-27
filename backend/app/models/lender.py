from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List
from .base import Base, RuleType


class Lender(Base):
    """Represents a financing company (e.g. Citizens Bank, Falcon Equipment Finance)."""
    __tablename__ = "lenders"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    programs: List["LenderProgram"] = relationship("LenderProgram", back_populates="lender")


class LenderProgram(Base):
    """
    A specific tier or program under a lender.
    Examples: Tier 1 / Tier 2 / Tier 3 from Stearns Bank [5], 
    Medical Program from Apex [4], or Standard Program from Falcon [2].
    """
    __tablename__ = "lender_programs"

    id = Column(Integer, primary_key=True)
    lender_id = Column(Integer, ForeignKey("lenders.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    min_loan_amount = Column(Integer)
    max_loan_amount = Column(Integer)
    typical_term_months = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    lender = relationship("Lender", back_populates="programs")
    rules: List["LenderProgramRule"] = relationship("LenderProgramRule", back_populates="program")


class LenderProgramRule(Base):
    """
    Core extensible rule table.
    This stores all rules parsed from the 5 PDFs (FICO, PayNet, TIB, 
    industry exclusions [5], bankruptcy years [2][3][5], state restrictions [1], etc.).
    Using rule_type + operator + value allows adding new rules from future PDFs
    without changing the database schema.
    """
    __tablename__ = "lender_program_rules"

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("lender_programs.id"), nullable=False)
    
    rule_type = Column(String(50), nullable=False)           # maps to RuleType enum
    operator = Column(String(20), nullable=False)            # "gte", "lte", "in", "not_in"
    value = Column(String(255))
    value_json = Column(JSON)                                 # for lists (e.g. excluded industries [5])
    priority = Column(Integer, default=100)
    failure_reason_template = Column(Text)                    # e.g. "Minimum FICO required is {threshold}, applicant has {actual}"
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    program = relationship("LenderProgram", back_populates="rules")