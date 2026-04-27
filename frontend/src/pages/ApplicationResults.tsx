// src/pages/ApplicationResults.tsx
import { useLocation, useParams } from 'react-router-dom';
import RuleResultTable from '../components/RuleResultTable';
import type { ApplicationMatch } from '../types';

const ApplicationResults = () => {
  const { applicationId } = useParams();
  const location = useLocation();
  const results: ApplicationMatch[] = location.state?.results || [];

  const eligible = results.filter(r => r.is_eligible);
  const notEligible = results.filter(r => !r.is_eligible);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Matching Results</h1>
      <p className="text-gray-600 mb-8">Application ID: {applicationId}</p>

      {/* Eligible Lenders */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold text-green-600 mb-4">
          ✅ Eligible Lenders ({eligible.length})
        </h2>
        {eligible.map(match => (
          <div key={match.id} className="bg-white border border-green-200 rounded-xl p-6 mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold">{match.lender_name} - {match.program_name}</h3>
                <p className="text-green-600 font-semibold">Fit Score: {match.fit_score}/100</p>
              </div>
              <span className="px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                APPROVED
              </span>
            </div>
            <RuleResultTable ruleResults={match.rule_results} />
          </div>
        ))}
      </div>

      {/* Not Eligible Lenders */}
      <div>
        <h2 className="text-2xl font-semibold text-red-600 mb-4">
          ❌ Not Eligible ({notEligible.length})
        </h2>
        {notEligible.map(match => (
          <div key={match.id} className="bg-white border border-red-200 rounded-xl p-6 mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold">{match.lender_name} - {match.program_name}</h3>
                <p className="text-red-600 font-semibold">Fit Score: {match.fit_score}/100</p>
              </div>
              <span className="px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                REJECTED
              </span>
            </div>
            <p className="text-red-600 mb-4 font-medium">{match.overall_reason}</p>
            <RuleResultTable ruleResults={match.rule_results} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ApplicationResults;