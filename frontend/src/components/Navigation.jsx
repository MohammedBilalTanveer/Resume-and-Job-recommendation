import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiSearch, FiBarChart2, FiSettings } from 'react-icons/fi';

export const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: FiHome },
    { path: '/analyzer', label: 'Resume Analyzer', icon: FiSearch },
    { path: '/jobs', label: 'Job Search', icon: FiBarChart2 },
  ];

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold flex items-center gap-2">
          📄 Resume ATS Scorer
        </Link>

        <div className="flex gap-6">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
                location.pathname === path
                  ? 'bg-white text-blue-600'
                  : 'hover:bg-blue-500'
              }`}
            >
              <Icon className="w-5 h-5" />
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};
