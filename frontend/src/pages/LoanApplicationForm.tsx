// src/pages/LoanApplicationForm.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import type { LoanApplication } from '../types';

const LoanApplicationForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
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
      // 1. create application
      setStatusText("Saving application...");
      const application = await api.createApplication(formData);

      // 2. trigger workflow
      setStatusText("Triggering Hatchet AI Engine...");
      await api.triggerUnderwriting(application.id);
      
      // 3. Polling to get result
      setStatusText("Engine running in background... Waiting for matches...");
      let results = null;
      let attempts = 0;
      const maxAttempts = 30; // wait max 30s

      while (!results && attempts < maxAttempts) {
        // hang for 1 second
        await new Promise(resolve => setTimeout(resolve, 1000));
        results = await api.getMatchResults(application.id);
        attempts++;
      }

      if (!results) {
        throw new Error("Underwriting is taking longer than expected. Please check back later.");
      }

      // 4. get the result and jump to result pages
      navigate(`/results/${application.id}`, { 
        state: { results, application } 
      });
      
    } catch (error: any) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
      setStatusText("");
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
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              {statusText}
            </span>
          ) : "Submit Application & Match Lenders"}
        </button>
      </form>
    </div>
  );
};

export default LoanApplicationForm;