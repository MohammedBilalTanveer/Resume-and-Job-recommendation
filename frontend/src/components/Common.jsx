import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const ATSScoreDisplay = ({ score }) => {
  const percentage = Math.round(score * 100);
  const getColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    if (score >= 0.4) return 'text-orange-600';
    return 'text-red-600';
  };

  const getBgColor = (score) => {
    if (score >= 0.8) return 'bg-green-100';
    if (score >= 0.6) return 'bg-yellow-100';
    if (score >= 0.4) return 'bg-orange-100';
    return 'bg-red-100';
  };

  return (
    <div className={`${getBgColor(score)} p-6 rounded-lg`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">ATS Score</p>
          <p className={`text-4xl font-bold ${getColor(score)}`}>{percentage}%</p>
        </div>
        <div className="w-24 h-24">
          <svg viewBox="0 0 36 36" className="w-full h-full">
            <circle cx="18" cy="18" r="15.915" fill="none" stroke="#ddd" strokeWidth="3" />
            <circle
              cx="18"
              cy="18"
              r="15.915"
              fill="none"
              stroke={getColor(score).replace('text-', '').replace('-600', '-500')}
              strokeWidth="3"
              strokeDasharray={`${percentage * 1.77} 177`}
              className="transform -rotate-90"
            />
            <text x="18" y="20" textAnchor="middle" className="text-sm font-bold" fill="#333">
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
    className={`inline-block px-3 py-1 rounded-full text-sm font-medium mr-2 mb-2 ${
      isMissing
        ? 'bg-red-100 text-red-800'
        : 'bg-green-100 text-green-800'
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
    <div className={`${sizeClass} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`} />
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
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis domain={[0, 100]} />
        <Tooltip formatter={(value) => `${value}%`} />
        <Bar dataKey="value" fill="#2563eb" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const JobCard = ({ job, onClick }) => (
  <div
    onClick={onClick}
    className="bg-white p-6 rounded-lg shadow hover:shadow-lg cursor-pointer transition-all"
  >
    <h3 className="text-lg font-bold text-gray-900">{job.title}</h3>
    <p className="text-sm text-gray-600 mt-1">{job.company}</p>
    <p className="text-sm text-gray-500 mt-2">{job.location}</p>
    <p className="text-sm text-gray-700 mt-3 line-clamp-2">{job.description}</p>
    <div className="mt-4 flex justify-between items-center">
      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
        {job.source}
      </span>
      <a
        href={job.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
      >
        View Job →
      </a>
    </div>
  </div>
);
