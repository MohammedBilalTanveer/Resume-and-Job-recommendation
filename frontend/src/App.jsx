import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Home } from './pages/Home';
import { Analyzer } from './pages/Analyzer';
import { Jobs } from './pages/Jobs';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { AuthCallback } from './pages/AuthCallback';
import { History } from './pages/History';
import useAuthStore from './store/authStore';
import './index.css';

function App() {
  const { initAuth } = useAuthStore();

  // Initialize auth on app load
  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <Router>
      <div className="min-h-screen bg-slate-900 text-slate-200">
        <Navigation />
        <main>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/auth/callback/:provider" element={<AuthCallback />} />
            
            {/* Protected routes */}
            <Route
              path="/analyzer"
              element={
                <ProtectedRoute>
                  <div className="max-w-7xl mx-auto px-4 py-24"><Analyzer /></div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/jobs"
              element={
                <ProtectedRoute>
                  <div className="max-w-7xl mx-auto px-4 py-24"><Jobs /></div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <div className="max-w-7xl mx-auto px-4 py-24"><History /></div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
