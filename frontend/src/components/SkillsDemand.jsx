import React, { useEffect, useState } from 'react';
import { jobsAPI } from '../api/client';
import { LoadingSpinner } from './Common';
import { FiBarChart2 } from 'react-icons/fi';

export const SkillsDemand = () => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSkillsDemand = async () => {
      try {
        const response = await jobsAPI.getSkillsDemand();
        setSkills(response.data.top_skills || []);
      } catch (err) {
        setError('Failed to load skills demand data');
      } finally {
        setLoading(false);
      }
    };

    fetchSkillsDemand();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="glass-card p-6 rounded-lg shadow border-none">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 text-white">
        <FiBarChart2 className="w-6 h-6 text-purple-400" />
        Most In-Demand Skills
      </h2>

      {error && (
        <div className="bg-red-500/10 text-red-400 p-4 rounded mb-4 border border-red-500/20">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {skills.map(([skill, count], idx) => (
          <div key={idx} className="flex items-center gap-4">
            <span className="font-medium text-sm text-slate-300 w-32 truncate">
              {skill.charAt(0).toUpperCase() + skill.slice(1)}
            </span>
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                style={{ width: `${(count / (skills[0]?.[1] || 1)) * 100}%` }}
              />
            </div>
            <span className="text-sm text-slate-400 font-medium">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};