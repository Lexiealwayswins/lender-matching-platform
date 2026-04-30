// src/utils/api.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  createApplication: async (data: any) => {
    const res = await fetch(`${API_BASE}/application/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create application');
    return res.json();
  },

  triggerUnderwriting: async (applicationId: number) => {
    const res = await fetch(`${API_BASE}/match/${applicationId}/underwrite`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Underwriting failed');
    return res.json(); 
  },

  getMatchResults: async (applicationId: number) => {
    const res = await fetch(`${API_BASE}/match/${applicationId}/matches`);
    // 如果返回 404，说明 Hatchet 后台还没算完，返回 null 继续等
    if (res.status === 404) return null; 
    if (!res.ok) throw new Error('Failed to fetch results');
    return res.json();
  },

  getAllPolicies: async () => {
    const res = await fetch(`${API_BASE}/lenders/`);
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },
};