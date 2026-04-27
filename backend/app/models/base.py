from sqlalchemy.orm import DeclarativeBase
import enum
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the Lender Matching Platform."""
    # pass
    __allow_unmapped__ = True # So that it allows List["xxx"] = relationship(...), not only Mapped[]


class RuleType(str, enum.Enum):
    """
    Enum for different types of credit rules extracted from lender PDFs.
    This design allows the system to support all rules found in the 5 PDFs
    without hard-coding columns.
    """
    MIN_FICO = "min_fico"
    MIN_PAYNET = "min_paynet"
    MIN_TIME_IN_BUSINESS = "min_time_in_business"
    MIN_LOAN_AMOUNT = "min_loan_amount"
    MAX_LOAN_AMOUNT = "max_loan_amount"
    MAX_EQUIPMENT_AGE = "max_equipment_age"
    MAX_MILEAGE = "max_mileage"
    EQUIPMENT_TYPE = "equipment_type"
    INDUSTRY_EXCLUSION = "industry_exclusion"
    STATE_RESTRICTION = "state_restriction"
    BANKRUPTCY_YEARS = "bankruptcy_years"
    MIN_REVENUE = "min_revenue"
    COLLATERAL_REQUIREMENT = "collateral_requirement"
    COMPARABLE_DEBT = "comparable_debt"
    REVOLVER_UTILIZATION = "revolver_utilization"
    OTHER = "other"