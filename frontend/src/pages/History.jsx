import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Clock, FileText, Trash2, ChevronRight, Loader2, Search, AlertCircle } from 'lucide-react';
import api from '../api/client';

export const History = () => {
  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/history/list', { params: { limit: 50 } });
      setAnalyses(response.data);
    } catch (err) {
      setError('Failed to load history');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this analysis?')) return;
    
    try {
      setDeletingId(id);
      await api.delete(`/history/${id}`);
      setAnalyses(analyses.filter(a => a.id !== id));
    } catch (err) {
      setError('Failed to delete analysis');
      console.error(err);
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score) => {
    if (!score) return 'text-slate-400';
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analysis History</h1>
          <p className="text-slate-400 mt-1">View and manage your past resume analyses</p>
        </div>
        <Link
          to="/analyzer"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2"
        >
          <Search className="w-4 h-4" />
          New Analysis
        </Link>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {analyses.length === 0 ? (
        <div className="bg-slate-800/50 rounded-xl p-12 text-center">
          <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No analyses yet</h3>
          <p className="text-slate-400 mb-6">
            Upload your first resume to get started with ATS scoring and job recommendations
          </p>
          <Link
            to="/analyzer"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Analyze Your Resume
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {analyses.map((analysis) => (
            <div
              key={analysis.id}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-5 hover:bg-slate-800/70 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <FileText className="w-5 h-5 text-blue-400" />
                    <h3 className="font-semibold text-white">
                      {analysis.filename || 'Untitled Analysis'}
                    </h3>
                    {analysis.ats_score && (
                      <span className={`px-2 py-0.5 rounded-full text-sm font-medium ${getScoreColor(analysis.ats_score)} bg-slate-700`}>
                        {Math.round(analysis.ats_score)}% Score
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-slate-400 mb-3">
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDate(analysis.created_at)}
                    </span>
                    {analysis.skills && analysis.skills.length > 0 && (
                      <span>{analysis.skills.length} skills detected</span>
                    )}
                  </div>

                  {analysis.skills && analysis.skills.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-3">
                      {analysis.skills.slice(0, 6).map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 text-xs bg-slate-700 text-slate-300 rounded"
                        >
                          {skill}
                        </span>
                      ))}
                      {analysis.skills.length > 6 && (
                        <span className="px-2 py-1 text-xs text-slate-500">
                          +{analysis.skills.length - 6} more
                        </span>
                      )}
                    </div>
                  )}

                  <p className="text-sm text-slate-400 line-clamp-2">
                    {analysis.resume_text.substring(0, 200)}...
                  </p>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  <Link
                    to={`/jobs?analysisId=${analysis.id}`}
                    className="px-3 py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg transition-colors text-sm"
                  >
                    Find Jobs
                  </Link>
                  <button
                    onClick={() => handleDelete(analysis.id)}
                    disabled={deletingId === analysis.id}
                    className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                    title="Delete analysis"
                  >
                    {deletingId === analysis.id ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Trash2 className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
