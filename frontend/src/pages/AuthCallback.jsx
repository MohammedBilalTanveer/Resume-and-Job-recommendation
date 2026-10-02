import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { Loader2, AlertCircle } from 'lucide-react';
import useAuthStore from '../store/authStore';

export const AuthCallback = () => {
  const navigate = useNavigate();
  const { provider } = useParams();
  const [searchParams] = useSearchParams();
  const { handleGoogleCallback, handleGitHubCallback } = useAuthStore();
  const [error, setError] = useState('');
  // OAuth codes are single-use; React StrictMode runs effects twice in development,
  // and a second exchange would fail and overwrite the successful login.
  const handledCode = useRef(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const errorParam = searchParams.get('error');

    if (code && handledCode.current === code) {
      return;
    }
    handledCode.current = code;

    if (errorParam) {
      setError(`Authentication failed: ${errorParam}`);
      return;
    }

    if (!code) {
      setError('No authorization code received');
      return;
    }

    const handleCallback = async () => {
      let result;
      
      if (provider === 'google') {
        result = await handleGoogleCallback(code);
      } else if (provider === 'github') {
        result = await handleGitHubCallback(code);
      } else {
        setError('Unknown OAuth provider');
        return;
      }

      if (result.success) {
        navigate('/analyzer', { replace: true });
      } else {
        setError(result.error || 'Authentication failed');
      }
    };

    handleCallback();
  }, [provider, searchParams, handleGoogleCallback, handleGitHubCallback, navigate]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Authentication Failed</h2>
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Completing sign in...</h2>
        <p className="text-slate-400">Please wait while we verify your account</p>
      </div>
    </div>
  );
};

export default AuthCallback;
