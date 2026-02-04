import React, { useState, useEffect } from 'react';
import { jobsAPI } from '../api/client';
import { useJobStore, useResumeStore } from '../store';
import { JobCard, LoadingSpinner } from './Common';
import { FiSearch, FiMapPin, FiTrendingUp } from 'react-icons/fi';

export const JobRecommendations = () => {
  const { recommendations, loading, setRecommendations, setLoading, setError } = useJobStore();
  const { resumeText } = useResumeStore();
  const [location, setLocation] = useState('remote');
  const [topK, setTopK] = useState(5);
  const [selectedJob, setSelectedJob] = useState(null);

  const handleRecommend = async () => {
    if (!resumeText) {
      setError('Please upload a resume first');
      return;
    }

    setLoading(true);
    try {
      const response = await jobsAPI.recommendJobs(resumeText, topK, location);
      setRecommendations(response.data.jobs);
    } catch (err) {
      setError('Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Controls */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <FiTrendingUp className="w-6 h-6 text-blue-600" />
          Job Recommendations
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FiMapPin className="inline mr-1" />
              Location
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., remote, New York"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Jobs
            </label>
            <input
              type="number"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              min="1"
              max="50"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleRecommend}
              disabled={loading || !resumeText}
              className="w-full py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Searching...
                </>
              ) : (
                <>
                  <FiSearch className="w-4 h-4" />
                  Get Recommendations
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Job Listings */}
      {recommendations.length > 0 && (
        <div>
          <p className="text-sm text-gray-600 mb-4">
            Found {recommendations.length} recommended jobs
          </p>
          <div className="grid grid-cols-1 gap-4">
            {recommendations.map((job, idx) => (
              <JobCard
                key={idx}
                job={job}
                onClick={() => setSelectedJob(job)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Selected Job Details */}
      {selectedJob && (
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-600">
          <h3 className="text-xl font-bold mb-2">{selectedJob.title}</h3>
          <p className="text-gray-600 mb-4">{selectedJob.company} • {selectedJob.location}</p>
          <div className="prose max-w-none">
            <p>{selectedJob.description}</p>
          </div>
          <div className="mt-4 flex gap-2">
            <a
              href={selectedJob.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Apply Now
            </a>
            <button
              onClick={() => setSelectedJob(null)}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
