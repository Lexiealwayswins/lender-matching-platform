// src/pages/LoanApplicationForm.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import type { LoanApplication } from '../types';

const LoanApplicationForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<LoanApplication>({
    business_name: '',
    industry: '',
    state: '',
    years_in_business: 0,
    annual_revenue: undefined,
    fico_score: 0,
    paynet_score: undefined,
    has_bankruptcy: false,
    bankruptcy_years_ago: undefined,
    requested_amount: 0,
    requested_term_months: 60,
    equipment_type: '',
    equipment_age_years: undefined,
    equipment_mileage: undefined,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const application = await api.createApplication(formData);
      const results = await api.runUnderwriting(application.id);
      
      navigate(`/results/${application.id}`, { 
        state: { results, application } 
      });
    } catch (error: any) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">New Equipment Finance Application</h1>
      <p className="text-gray-600 mb-8">Fill in the details to test backend matching engine</p>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow p-8 space-y-8">
        {/* Business Information */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Business Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <input type="text" placeholder="Business Name" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, business_name: e.target.value})} required />
            <input type="text" placeholder="Industry (e.g. Construction)" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, industry: e.target.value})} required />
          </div>
        </div>

        {/* Credit Information */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Credit Information</h2>
          <div className="grid grid-cols-3 gap-4">
            <input type="number" placeholder="FICO Score" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, fico_score: Number(e.target.value)})} required />
            <input type="number" placeholder="PayNet Score" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, paynet_score: Number(e.target.value)})} />
            <input type="number" placeholder="Years in Business" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, years_in_business: Number(e.target.value)})} required />
          </div>
        </div>

        {/* Loan Request */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Loan Request</h2>
          <div className="grid grid-cols-3 gap-4">
            <input type="number" placeholder="Requested Amount ($)" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, requested_amount: Number(e.target.value)})} required />
            <input type="text" placeholder="Equipment Type" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, equipment_type: e.target.value})} required />
            <input type="number" placeholder="Equipment Age (years)" className="p-3 border rounded-lg" 
              onChange={(e) => setFormData({...formData, equipment_age_years: Number(e.target.value)})} />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-xl text-lg disabled:opacity-70"
        >
          {loading ? "Submitting & Running Matching Engine..." : "Submit Application & Match Lenders"}
        </button>
      </form>
    </div>
  );
};

export default LoanApplicationForm;