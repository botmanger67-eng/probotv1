import React, { ErrorInfo, ReactNode } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ProjectList from './components/ProjectList';
import AdminPanel from './components/AdminPanel';
import Billing from './components/Billing';

// ---------------------------------------------------------------------------
// Error Boundary for catching rendering errors globally
// ---------------------------------------------------------------------------
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<{ children: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // In production, send this to an external logging service (e.g., Sentry)
    console.error('Uncaught error:', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
          <h2 className="text-2xl font-bold mb-4">Something went wrong</h2>
          <p className="text-gray-400 mb-6">{this.state.error?.message || 'Unknown error'}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
          >
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ---------------------------------------------------------------------------
// Navigation bar using Tailwind CSS (consistent with tailwind.config.js)
// ---------------------------------------------------------------------------
const NavigationBar: React.FC = () => {
  return (
    <nav className="bg-gray-800 text-white p-4 shadow-md">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex space-x-4">
          <Link to="/dashboard" className="hover:text-blue-400 transition-colors">
            Dashboard
          </Link>
          <Link to="/projects" className="hover:text-blue-400 transition-colors">
            Projects
          </Link>
          <Link to="/admin" className="hover:text-blue-400 transition-colors">
            Admin
          </Link>
          <Link to="/billing" className="hover:text-blue-400 transition-colors">
            Billing
          </Link>
        </div>
      </div>
    </nav>
  );
};

// ---------------------------------------------------------------------------
// Main App component
// ---------------------------------------------------------------------------
const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <NavigationBar />
        <main className="container mx-auto p-4">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/projects" element={<ProjectList />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/billing" element={<Billing />} />
            {/* Fallback for unknown routes */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;