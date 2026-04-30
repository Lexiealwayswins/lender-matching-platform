from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base
from .match import ApplicationMatch
from datetime import datetime


class LoanApplication(Base):
    """
    Represents a single loan application submitted by a broker or business.
    Contains all data points needed to evaluate against lender rules:
    FICO, PayNet, TIB, industry, state, requested amount, equipment details, etc.
    This is the "input" for the matching engine.
    """
    __tablename__ = "loan_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_number: Mapped[str] = mapped_column(String(50), unique=True)
    
    # Borrower / Business Info
    business_name: Mapped[str] = mapped_column(String(200))
    industry: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(2))
    years_in_business: Mapped[int | None] = mapped_column()
    annual_revenue: Mapped[int | None] = mapped_column()
    
    # Credit Info
    fico_score: Mapped[int | None] = mapped_column()
    paynet_score: Mapped[int | None] = mapped_column()
    has_bankruptcy: Mapped[bool | None] = mapped_column(default=False)
    bankruptcy_years_ago: Mapped[int | None] = mapped_column()
    has_judgements: Mapped[bool | None] = mapped_column(default=False)
    has_repossessions: Mapped[bool | None] = mapped_column(default=False)
    highest_previous_debt: Mapped[int | None] = mapped_column()
    
    # Loan Request
    requested_amount: Mapped[int] = mapped_column()
    requested_term_months: Mapped[int | None] = mapped_column()
    equipment_type: Mapped[str | None] = mapped_column(String(100))
    equipment_age_years: Mapped[int | None] = mapped_column()
    equipment_mileage: Mapped[int | None] = mapped_column()
    
    # Metadata
    status: Mapped[str | None] = mapped_column(String(50), default="draft")
    submitted_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    matches: Mapped[list["ApplicationMatch"]] = relationship(back_populates="application")