from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List
from .base import Base
from .match import ApplicationMatch


class LoanApplication(Base):
    """
    Represents a single loan application submitted by a broker or business.
    Contains all data points needed to evaluate against lender rules:
    FICO, PayNet, TIB, industry, state, requested amount, equipment details, etc.
    This is the "input" for the matching engine.
    """
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True)
    application_number = Column(String(50), unique=True, nullable=False)
    
    # Borrower / Business Info
    business_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    state = Column(String(2), nullable=False)
    years_in_business = Column(Integer)
    annual_revenue = Column(Integer)
    
    # Credit Info
    fico_score = Column(Integer)
    paynet_score = Column(Integer)
    has_bankruptcy = Column(Boolean, default=False)
    bankruptcy_years_ago = Column(Integer)
    has_judgements = Column(Boolean, default=False)
    has_repossessions = Column(Boolean, default=False)
    
    # Loan Request
    requested_amount = Column(Integer, nullable=False)
    requested_term_months = Column(Integer)
    equipment_type = Column(String(100))
    equipment_age_years = Column(Integer)
    equipment_mileage = Column(Integer)
    
    # Metadata
    status = Column(String(50), default="draft")
    submitted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    matches: List["ApplicationMatch"] = relationship("ApplicationMatch", back_populates="application")