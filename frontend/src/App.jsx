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
      <div className="min-h-screen bg-slate-900 text-slate-200">
        <Navigation />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analyzer" element={<div className="max-w-7xl mx-auto px-4 py-24"><Analyzer /></div>} />
            <Route path="/jobs" element={<div className="max-w-7xl mx-auto px-4 py-24"><Jobs /></div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
