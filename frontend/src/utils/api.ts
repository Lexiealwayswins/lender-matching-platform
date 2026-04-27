// src/utils/api.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  // Create new loan application
  createApplication: async (data: any) => {
    const res = await fetch(`${API_BASE}/loans/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create application');
    return res.json();
  },

  // Run underwriting / matching engine
  runUnderwriting: async (applicationId: number) => {
    const res = await fetch(`${API_BASE}/loans/${applicationId}/underwrite`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Underwriting failed');
    return res.json();
  },

  // Get previous match results
  getMatchResults: async (applicationId: number) => {
    const res = await fetch(`${API_BASE}/loans/${applicationId}/matches`);
    if (!res.ok) throw new Error('Failed to fetch results');
    return res.json();
  },

  // Get all lender policies
  getAllPolicies: async () => {
    const res = await fetch(`${API_BASE}/policies/lenders`);
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },
};