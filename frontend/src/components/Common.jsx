import React from 'react';
import DOMPurify from 'dompurify';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// SafeHTML component to sanitize and render HTML content
export const SafeHTML = ({ html, className = '', truncate = false }) => {
  if (!html) return null;
  
  const sanitized = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'b', 'em', 'i', 'ul', 'ol', 'li', 'a', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
  
  // For truncated preview, strip HTML and show plain text
  if (truncate) {
    const plainText = sanitized.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    return <span className={className}>{plainText}</span>;
  }
  
  return (
    <div 
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitized }}
    />
  );
};

export const ATSScoreDisplay = ({ score }) => {
  const percentage = Math.round(score * 100);
  const getColor = (score) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-yellow-400';
    if (score >= 0.4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getBgColor = (score) => {
    if (score >= 0.8) return 'bg-green-500/10 border-green-500/20';
    if (score >= 0.6) return 'bg-yellow-500/10 border-yellow-500/20';
    if (score >= 0.4) return 'bg-orange-500/10 border-orange-500/20';
    return 'bg-red-500/10 border-red-500/20';
  };

  const getStrokeColor = (score) => {
    if (score >= 0.8) return '#4ade80';
    if (score >= 0.6) return '#facc15';
    if (score >= 0.4) return '#fb923c';
    return '#f87171';
  }

  return (
    <div className={`${getBgColor(score)} p-6 rounded-lg border`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">ATS Score</p>
          <p className={`text-4xl font-bold ${getColor(score)}`}>{percentage}%</p>
        </div>
        <div className="w-24 h-24">
          <svg viewBox="0 0 36 36" className="w-full h-full">
            <circle cx="18" cy="18" r="15.915" fill="none" stroke="#334155" strokeWidth="3" />
            <circle
              cx="18"
              cy="18"
              r="15.915"
              fill="none"
              stroke={getStrokeColor(score)}
              strokeWidth="3"
              strokeDasharray={`${percentage * 1.77} 177`}
              className="transform -rotate-90 origin-center transition-all duration-1000 ease-out"
            />
            <text x="18" y="20" textAnchor="middle" className="text-[8px] font-bold fill-white">
              {percentage}%
            </text>
          </svg>
        </div>
      </div>
    </div>
  );
};

export const KeywordBadge = ({ keyword, isMissing = false }) => (
  <span
    className={`inline-block px-3 py-1 rounded-full text-sm font-medium mr-2 mb-2 ${isMissing
      ? 'bg-red-500/10 text-red-400 border border-red-500/20'
      : 'bg-green-500/10 text-green-400 border border-green-500/20'
      }`}
  >
    {keyword}
    {isMissing && <span className="ml-1">✗</span>}
  </span>
);

export const LoadingSpinner = ({ size = 'md' }) => {
  const sizeClass = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }[size];

  return (
    <div className={`${sizeClass} border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin`} />
  );
};

export const ScoreBreakdown = ({ breakdown }) => {
  const data = Object.entries(breakdown).map(([key, value]) => ({
    name: key.replace(/_/g, ' ').toUpperCase(),
    value: Math.round(value * 100),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="name" stroke="#94a3b8" />
        <YAxis domain={[0, 100]} stroke="#94a3b8" />
        <Tooltip
          formatter={(value) => `${value}%`}
          contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
          itemStyle={{ color: '#f1f5f9' }}
        />
        <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const JobCard = ({ job, onClick }) => (
  <div
    onClick={onClick}
    className="glass-card p-6 rounded-lg shadow hover:shadow-lg hover:border-blue-500/50 cursor-pointer transition-all border border-white/5 active:scale-[0.99] bg-white/5 group"
  >
    <h3 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">{job.title}</h3>
    <p className="text-sm text-slate-400 mt-1">{job.company}</p>
    <p className="text-sm text-slate-500 mt-2">{job.location}</p>
    <p className="text-sm text-slate-300 mt-3 line-clamp-2">
      <SafeHTML html={job.description} truncate={true} />
    </p>
    <div className="mt-4 flex justify-between items-center">
      <span className="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-1 rounded">
        {job.source}
      </span>
      <span className="text-blue-400 group-hover:text-blue-300 text-sm font-medium flex items-center gap-1">
        View Job <span className="group-hover:translate-x-1 transition-transform">→</span>
      </span>
    </div>
  </div>
);
