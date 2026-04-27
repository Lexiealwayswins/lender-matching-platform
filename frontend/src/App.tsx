// src/App.tsx
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import LoanApplicationForm from './pages/LoanApplicationForm';
import ApplicationResults from './pages/ApplicationResults';
import LenderPolicies from './pages/LenderPolicies';

/**
 * Main application component with routing.
 * This fulfills the UI requirements:
 * - Loan application form
 * - Results display with detailed rule-by-rule breakdown
 * - Lender policy management screen
 */
function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow border-b sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <div className="flex items-center gap-10">
              <h1 className="text-2xl font-bold text-blue-700">LenderMatch</h1>
              <div className="flex gap-8 text-sm font-medium">
                <Link to="/" className="hover:text-blue-600">New Application</Link>
                <Link to="/policies" className="hover:text-blue-600">Lender Policies</Link>
              </div>
            </div>
            <div className="text-xs text-gray-500">Engineering Assignment Demo</div>
          </div>
        </nav>

        <main className="max-w-6xl mx-auto py-8">
          <Routes>
            <Route path="/" element={<LoanApplicationForm />} />
            <Route path="/results/:applicationId" element={<ApplicationResults />} />
            <Route path="/policies" element={<LenderPolicies />} />
          </Routes>
        </main>

        <footer className="bg-white border-t py-6 text-center text-xs text-gray-500 mt-12">
          Lender Matching Platform • FastAPI + React + TypeScript + Tailwind
        </footer>
      </div>
    </Router>
  );
}

export default App;