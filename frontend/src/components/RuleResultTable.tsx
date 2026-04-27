// src/components/RuleResultTable.tsx
import type { MatchRuleResult } from '../types';

interface Props {
  ruleResults: MatchRuleResult[];
}

const RuleResultTable = ({ ruleResults }: Props) => {
  return (
    <div className="mt-4">
      <h4 className="font-semibold mb-3 text-gray-700">Rule Evaluation Details</h4>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="text-left p-3 border">Rule Type</th>
              <th className="text-left p-3 border">Expected</th>
              <th className="text-left p-3 border">Actual</th>
              <th className="text-left p-3 border">Result</th>
              <th className="text-left p-3 border w-2/5">Reason</th>
            </tr>
          </thead>
          <tbody>
            {ruleResults.map((rule, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="p-3 font-medium">{rule.rule_type.replace('_', ' ').toUpperCase()}</td>
                <td className="p-3">{rule.expected_value}</td>
                <td className="p-3">{rule.actual_value}</td>
                <td className="p-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    rule.passed 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {rule.passed ? 'PASSED' : 'FAILED'}
                  </span>
                </td>
                <td className="p-3 text-sm text-gray-600">{rule.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RuleResultTable;