import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { jobsAPI, historyAPI } from '../api/client';
import { useJobStore, useResumeStore } from '../store';
import { JobCard, LoadingSpinner, SafeHTML } from './Common';
import { FiSearch, FiMapPin, FiTrendingUp, FiFileText, FiAlertCircle } from 'react-icons/fi';

export const JobRecommendations = () => {
  const [searchParams] = useSearchParams();
  const { recommendations, loading, setRecommendations, setLoading, setError } = useJobStore();
  const { resumeText } = useResumeStore();
  const [location, setLocation] = useState('remote');
  const [topK, setTopK] = useState(5);
  const [selectedJob, setSelectedJob] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState('');
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [extractedSkills, setExtractedSkills] = useState([]);

  // Fetch user's previous analyses on mount
  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        const response = await historyAPI.listAnalyses(0, 20);
        setAnalyses(response.data);
        
        // Check for analysisId in URL params
        const analysisIdParam = searchParams.get('analysisId');
        if (analysisIdParam) {
          setSelectedAnalysisId(analysisIdParam);
        } else if (response.data.length > 0 && !resumeText) {
          // Auto-select latest if no current resume
          setSelectedAnalysisId(response.data[0].id.toString());
        }
      } catch (err) {
        console.error('Failed to fetch history:', err);
      } finally {
        setLoadingHistory(false);
      }
    };
    
    fetchAnalyses();
  }, [searchParams, resumeText]);

  // Get the active resume text (current or from selected analysis)
  const getActiveResumeText = () => {
    if (resumeText) return resumeText;
    
    if (selectedAnalysisId) {
      const analysis = analyses.find(a => a.id.toString() === selectedAnalysisId);
      return analysis?.resume_text || '';
    }
    
    return '';
  };

  const handleRecommend = async () => {
    const activeText = getActiveResumeText();
    
    if (!activeText) {
      setError('Please upload a resume first');
      return;
    }

    setLoading(true);
    try {
      const response = await jobsAPI.recommendJobs(activeText, topK, location);
      setRecommendations(response.data.jobs);
      setExtractedSkills(response.data.extracted_skills || []);
    } catch (err) {
      setError('Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const hasResumeData = resumeText || analyses.length > 0;

  if (loadingHistory) {
    return (
      <div className="glass-card p-8 rounded-lg shadow text-center">
        <LoadingSpinner size="lg" />
        <p className="text-slate-400 mt-4">Loading your resume data...</p>
      </div>
    );
  }

  // Show prompt if no resume data
  if (!hasResumeData) {
    return (
      <div className="glass-card p-8 rounded-lg shadow text-center">
        <FiAlertCircle className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">No Resume Analyzed Yet</h2>
        <p className="text-slate-400 mb-6 max-w-md mx-auto">
          To get personalized job recommendations, please analyze your resume first. 
          Our AI will extract your skills and match you with relevant job opportunities.
        </p>
        <Link
          to="/analyzer"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <FiFileText className="w-5 h-5" />
          Analyze Your Resume
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Controls */}
      <div className="glass-card p-6 rounded-lg shadow border-none">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-white">
          <FiTrendingUp className="w-6 h-6 text-blue-400" />
          Job Recommendations
        </h2>

        {/* Resume Selection (if user has history) */}
        {analyses.length > 0 && !resumeText && (
          <div className="mb-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              <FiFileText className="inline mr-1" />
              Select Resume to Use
            </label>
            <select
              value={selectedAnalysisId}
              onChange={(e) => setSelectedAnalysisId(e.target.value)}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 text-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="">Select a resume...</option>
              {analyses.map((analysis) => (
                <option key={analysis.id} value={analysis.id}>
                  {analysis.filename || 'Untitled'} - {new Date(analysis.created_at).toLocaleDateString()}
                  {analysis.ats_score ? ` (${Math.round(analysis.ats_score)}% score)` : ''}
                </option>
              ))}
            </select>
            <p className="text-xs text-slate-500 mt-1">
              Or <Link to="/analyzer" className="text-blue-400 hover:underline">upload a new resume</Link>
            </p>
          </div>
        )}

        {resumeText && (
          <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
            <p className="text-sm text-green-400 flex items-center gap-2">
              <FiFileText className="w-4 h-4" />
              Using your currently uploaded resume
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              <FiMapPin className="inline mr-1" />
              Location
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., remote, New York"
              className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 text-slate-200 rounded-lg focus:outline-none focus:border-blue-500 placeholder-slate-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Number of Jobs
            </label>
            <input
              type="number"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              min="1"
              max="50"
              className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 text-slate-200 rounded-lg focus:outline-none focus:border-blue-500 placeholder-slate-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleRecommend}
              disabled={loading || !getActiveResumeText()}
              className="w-full py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 transition flex items-center justify-center gap-2"
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

      {/* Extracted Skills */}
      {extractedSkills.length > 0 && (
        <div className="glass-card p-4 rounded-lg shadow border-none">
          <p className="text-sm text-slate-400 mb-2">Skills used for matching:</p>
          <div className="flex flex-wrap gap-2">
            {extractedSkills.map((skill, idx) => (
              <span key={idx} className="px-3 py-1 bg-blue-500/20 text-blue-400 text-sm rounded-full">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Job Listings */}
      {recommendations.length > 0 && (
        <div>
          <p className="text-sm text-slate-400 mb-4">
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
        <div className="glass-card p-6 rounded-lg shadow border-l-4 border-blue-500 relative">
          <h3 className="text-xl font-bold mb-2 text-white">{selectedJob.title}</h3>
          <p className="text-slate-400 mb-4">{selectedJob.company} • {selectedJob.location}</p>
          <div className="prose prose-invert max-w-none text-slate-300">
            <SafeHTML html={selectedJob.description} />
          </div>
          <div className="mt-4 flex gap-2">
            <a
              href={selectedJob.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Apply Now
            </a>
            <button
              onClick={() => setSelectedJob(null)}
              className="px-4 py-2 bg-slate-700 text-slate-200 rounded-lg hover:bg-slate-600 transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
