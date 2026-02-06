import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Search, BarChart2, Menu, X } from 'lucide-react';

export const Navigation = () => {
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/analyzer', label: 'Resume Analyzer', icon: Search },
    { path: '/jobs', label: 'Job Search', icon: BarChart2 },
  ];

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-slate-900/90 backdrop-blur-md shadow-lg py-2' : 'bg-transparent py-4'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold flex items-center gap-2 text-white">
          <span className="bg-gradient-to-r from-blue-500 to-purple-500 w-8 h-8 rounded-lg flex items-center justify-center">
            📄
          </span>
          <span className="hidden sm:inline">CareerPilot</span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-8">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`nav-link flex items-center gap-2 px-1 py-1 ${location.pathname === path ? 'text-white font-semibold' : 'text-slate-300'
                }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
          <Link to="/analyzer" className="btn-primary py-2 px-5 text-sm">
            Get Started
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button
          className="md:hidden text-white p-2"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 w-full bg-slate-900 border-t border-slate-800 p-4 shadow-xl">
          <div className="flex flex-col space-y-4">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg ${location.pathname === path ? 'bg-blue-600/20 text-blue-400' : 'text-slate-300 hover:bg-slate-800'
                  }`}
                onClick={() => setMobileMenuOpen(false)}
              >
                <Icon className="w-5 h-5" />
                {label}
              </Link>
            ))}
            <Link to="/resume-upload" className="btn-primary text-center" onClick={() => setMobileMenuOpen(false)}>
              Get Started
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};
