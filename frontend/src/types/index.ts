// src/types/index.ts
export interface LoanApplication {
  business_name: string;
  industry: string;
  state: string;
  years_in_business: number;
  annual_revenue?: number;
  fico_score: number;
  paynet_score?: number;
  has_bankruptcy: boolean;
  bankruptcy_years_ago?: number;
  requested_amount: number;
  requested_term_months?: number;
  equipment_type: string;
  equipment_age_years?: number;
  equipment_mileage?: number;
}

export interface MatchRuleResult {
  rule_type: string;
  passed: boolean;
  actual_value: string;
  expected_value: string;
  reason: string;
}

export interface ApplicationMatch {
  id: number;
  program_id: number;
  lender_name: string;
  program_name: string;
  is_eligible: boolean;
  fit_score: number;
  overall_reason: string;
  rule_results: MatchRuleResult[];
}

export interface LenderPolicy {
  id: number;
  name: string;
  description: string;
  programs: LenderProgram[];
}

export interface LenderProgram {
  id: number;
  name: string;
  description: string;
  min_loan_amount?: number;
  max_loan_amount?: number;
  rules: any[];
}