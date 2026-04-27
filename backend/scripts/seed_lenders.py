# scripts/seed_lenders.py
import sys
from pathlib import Path

# Fix: Make sure Python can find the 'app' module
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import RuleType
from app.models.lender import Lender, LenderProgram, LenderProgramRule
from app.models.match import ApplicationMatch, MatchRuleResult
from app.models.application import LoanApplication

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()


def seed_data():
    """
    Complete seed script with proper cleanup order to avoid foreign key violations.
    Creates 5 lenders with multiple realistic programs based on the 5 PDFs.
    """
    print("🗑️ Clearing existing data...")

    # Must delete in correct order to respect foreign key constraints
    db.query(MatchRuleResult).delete()
    db.query(ApplicationMatch).delete()
    db.query(LoanApplication).delete()
    db.query(LenderProgramRule).delete()
    db.query(LenderProgram).delete()
    db.query(Lender).delete()
    db.commit()

    print("✅ Database cleared. Starting seeding...")

    # ==================== 1. Citizens Bank ====================
    citizens = Lender(name="Citizens Bank", description="2025 Equipment Finance Program")
    db.add(citizens)
    db.flush()

    c_tier1 = LenderProgram(
        lender_id=citizens.id,
        name="Tier 1 - General",
        description="$75,000 ALL IN",
        min_loan_amount=0,
        max_loan_amount=75000,
        typical_term_months=60
    )
    c_tier2 = LenderProgram(
        lender_id=citizens.id,
        name="Tier 2 - Startup",
        description="$50,000 ALL IN - Higher Risk",
        min_loan_amount=0,
        max_loan_amount=50000,
        typical_term_months=48
    )
    c_tier3 = LenderProgram(
        lender_id=citizens.id,
        name="Tier 3 - Large",
        description="$75K - $1M with full financials",
        min_loan_amount=75000,
        max_loan_amount=1000000,
        typical_term_months=60
    )
    db.add_all([c_tier1, c_tier2, c_tier3])
    db.flush()

    db.add_all([
        LenderProgramRule(program_id=c_tier1.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="700", failure_reason_template="Minimum FICO required is {threshold}, applicant has {actual}", priority=10),
        LenderProgramRule(program_id=c_tier1.id, rule_type=RuleType.BANKRUPTCY_YEARS.value, operator="gte", value="5", failure_reason_template="Bankruptcy must be discharged at least 5 years ago", priority=20),
        LenderProgramRule(program_id=c_tier1.id, rule_type=RuleType.MIN_TIME_IN_BUSINESS.value, operator="gte", value="2", failure_reason_template="Minimum 2 years in business required", priority=30),
        LenderProgramRule(program_id=c_tier2.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="720", failure_reason_template="Tier 2 requires minimum FICO {threshold}", priority=10),
        LenderProgramRule(program_id=c_tier3.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="710", failure_reason_template="Tier 3 requires minimum FICO {threshold}", priority=10),
    ])

    # ==================== 2. Falcon Equipment Finance ====================
    falcon = Lender(name="Falcon Equipment Finance", description="Rates & Programs November 2025")
    db.add(falcon)
    db.flush()

    f_standard = LenderProgram(lender_id=falcon.id, name="Standard Program", description="App-only up to $350k", min_loan_amount=15000, max_loan_amount=350000)
    f_trucking = LenderProgram(lender_id=falcon.id, name="Trucking Program", description="Specialized for trucking", min_loan_amount=25000, max_loan_amount=300000)
    db.add_all([f_standard, f_trucking])
    db.flush()

    db.add_all([
        LenderProgramRule(program_id=f_standard.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="680", failure_reason_template="Minimum FICO required is {threshold}", priority=10),
        LenderProgramRule(program_id=f_standard.id, rule_type=RuleType.MIN_PAYNET.value, operator="gte", value="660", failure_reason_template="Minimum PayNet required is {threshold}", priority=20),
        LenderProgramRule(program_id=f_standard.id, rule_type=RuleType.MIN_TIME_IN_BUSINESS.value, operator="gte", value="3", failure_reason_template="Minimum 3 years in business required", priority=30),
        LenderProgramRule(program_id=f_trucking.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="700", failure_reason_template="Trucking requires higher FICO {threshold}", priority=10),
    ])

    # ==================== 3. Advantage+ Financing ====================
    advantage = Lender(name="Advantage+ Financing", description="Broker ICP $75K non-trucking")
    db.add(advantage)
    db.flush()

    a_nontruck = LenderProgram(lender_id=advantage.id, name="Non-Trucking $75K", description="Main Program", max_loan_amount=75000)
    a_startup = LenderProgram(lender_id=advantage.id, name="Startup Program", description="Higher risk startups", max_loan_amount=50000)
    db.add_all([a_nontruck, a_startup])
    db.flush()

    db.add_all([
        LenderProgramRule(program_id=a_nontruck.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="680", failure_reason_template="Minimum FICO 680 required", priority=10),
        LenderProgramRule(program_id=a_startup.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="700", failure_reason_template="Startup requires FICO 700+", priority=10),
        LenderProgramRule(program_id=a_nontruck.id, rule_type=RuleType.BANKRUPTCY_YEARS.value, operator="lte", value="0", failure_reason_template="No previous bankruptcies allowed", priority=30),
    ])

    # ==================== 4. Apex Commercial Capital ====================
    apex = Lender(name="Apex Commercial Capital", description="Broker Guidelines")
    db.add(apex)
    db.flush()

    apex_std = LenderProgram(lender_id=apex.id, name="Standard Program", description="Main credit box", max_loan_amount=500000)
    apex_medical = LenderProgram(lender_id=apex.id, name="Medical Equipment Program", description="Specialized for medical", max_loan_amount=750000)
    db.add_all([apex_std, apex_medical])
    db.flush()

    db.add_all([
        LenderProgramRule(program_id=apex_std.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="670", failure_reason_template="Minimum FICO required is {threshold}", priority=10),
        LenderProgramRule(program_id=apex_std.id, rule_type=RuleType.STATE_RESTRICTION.value, operator="not_in", value_json=["CA", "NV", "ND", "VT"], failure_reason_template="State {actual} is restricted", priority=20),
        LenderProgramRule(program_id=apex_medical.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="690", failure_reason_template="Medical program requires FICO {threshold}", priority=10),
    ])

    # ==================== 5. Stearns Bank ====================
    stearns = Lender(name="Stearns Bank", description="Equipment Finance Credit Box 4.14.2025")
    db.add(stearns)
    db.flush()

    s_tier1 = LenderProgram(lender_id=stearns.id, name="Tier 1", description="Highest credit tier", max_loan_amount=999999)
    s_tier2 = LenderProgram(lender_id=stearns.id, name="Tier 2", description="Medium credit tier", max_loan_amount=500000)
    db.add_all([s_tier1, s_tier2])
    db.flush()

    db.add_all([
        LenderProgramRule(program_id=s_tier1.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="725", failure_reason_template="Tier 1 requires minimum FICO {threshold}", priority=10),
        LenderProgramRule(program_id=s_tier1.id, rule_type=RuleType.MIN_PAYNET.value, operator="gte", value="685", failure_reason_template="Tier 1 requires minimum PayNet {threshold}", priority=20),
        LenderProgramRule(program_id=s_tier1.id, rule_type=RuleType.INDUSTRY_EXCLUSION.value, operator="not_in", value_json=["Restaurants", "Car Wash", "Gaming", "Oil & Gas", "Cannabis"], failure_reason_template="Industry '{actual}' is not allowed", priority=30),
        LenderProgramRule(program_id=s_tier2.id, rule_type=RuleType.MIN_FICO.value, operator="gte", value="700", failure_reason_template="Tier 2 requires minimum FICO {threshold}", priority=10),
    ])

    db.commit()
    print("✅ Seed data successfully loaded!")
    print("   Created 5 Lenders with multiple programs each (Tier 1, Tier 2, Standard, Medical, etc.).")
    print("   You can now view them in the Lender Policies page.")


if __name__ == "__main__":
    seed_data()