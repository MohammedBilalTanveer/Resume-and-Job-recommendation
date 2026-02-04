import React, { useEffect, useState } from 'react';
import { jobsAPI } from '../api/client';
import { LoadingSpinner } from './Common';
import { FiBarChart2, FiTrendingUp } from 'react-icons/fi';

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
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <FiBarChart2 className="w-6 h-6 text-purple-600" />
        Most In-Demand Skills
      </h2>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded mb-4">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {skills.map(([skill, count], idx) => (
          <div key={idx} className="flex items-center gap-4">
            <span className="font-medium text-sm text-gray-700 w-32 truncate">
              {skill.charAt(0).toUpperCase() + skill.slice(1)}
            </span>
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                style={{ width: `${(count / (skills[0]?.[1] || 1)) * 100}%` }}
              />
            </div>
            <span className="text-sm text-gray-600 font-medium">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
