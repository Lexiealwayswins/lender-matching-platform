// src/pages/LenderPolicies.tsx
import { useState, useEffect } from 'react';
import { api } from '../utils/api';
import type { LenderPolicy } from '../types';

const LenderPolicies = () => {
  const [policies, setPolicies] = useState<LenderPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log("🔄 Fetching policies from:", `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/policies/lenders`);
      
      const data = await api.getAllPolicies();
      console.log("✅ Policies loaded successfully:", data);
      
      setPolicies(data);
    } catch (err: any) {
      console.error("❌ Failed to load policies:", err);
      setError(`Failed to load policies: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="text-lg">Loading lender policies from database...</div>
        <div className="text-sm text-gray-500 mt-2">Please wait while fetching from backend</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-12 text-center text-red-600">
        <p className="text-xl font-medium">{error}</p>
        <p className="mt-4 text-sm text-gray-600">
          Please check that backend is running on port 8000 and try refreshing.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Lender Policy Management</h1>
          <p className="text-gray-600 mt-1">
            Showing rules extracted from the 5 PDF documents
          </p>
        </div>
        <button
          onClick={fetchPolicies}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
        >
          Refresh
        </button>
      </div>

      {policies.map((lender) => (
        <div key={lender.id} className="mb-10 bg-white rounded-2xl shadow overflow-hidden">
          <div className="bg-gradient-to-r from-blue-700 to-indigo-600 text-white p-6">
            <h2 className="text-2xl font-bold">{lender.name}</h2>
            <p className="text-blue-100 mt-1">{lender.description}</p>
          </div>

          <div className="p-6">
            {lender.programs.map((program) => (
              <div key={program.id} className="mb-8 border border-gray-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4 text-gray-800">
                  {program.name}
                  {program.max_loan_amount && (
                    <span className="ml-3 text-blue-600 text-sm font-normal">
                      (Max: ${program.max_loan_amount.toLocaleString()})
                    </span>
                  )}
                </h3>

                <div className="space-y-3">
                  {program.rules.map((rule: any, index: number) => (
                    <div key={index} className="bg-gray-50 p-4 rounded-lg flex items-center border border-gray-100">
                      <div className="flex-1">
                        <span className="font-mono text-xs bg-white px-3 py-1 rounded border text-blue-700">
                          {rule.rule_type}
                        </span>
                        <span className="ml-4 text-gray-700">
                          {rule.operator} <span className="font-medium">{rule.value || JSON.stringify(rule.value_json)}</span>
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        Priority: {rule.priority}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default LenderPolicies;