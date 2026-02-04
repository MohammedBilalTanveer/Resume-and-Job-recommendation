import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { Home } from './pages/Home';
import { Analyzer } from './pages/Analyzer';
import { Jobs } from './pages/Jobs';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analyzer" element={<Analyzer />} />
            <Route path="/jobs" element={<Jobs />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
