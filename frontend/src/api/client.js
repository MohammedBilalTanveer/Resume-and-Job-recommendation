import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to get token from localStorage (zustand persist storage)
const getStoredToken = () => {
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsed = JSON.parse(authStorage);
      return parsed?.state?.accessToken || null;
    }
  } catch (e) {
    console.error('Error reading auth token from storage:', e);
  }
  return null;
};

// Add request interceptor to automatically include auth token
api.interceptors.request.use(
  (config) => {
    // Get token from axios defaults (set by setAuth) or localStorage (for page refresh)
    const defaultToken = api.defaults.headers.common['Authorization'];
    const storedToken = getStoredToken();
    
    // Use default token if available, otherwise fall back to stored token
    const token = defaultToken || (storedToken ? `Bearer ${storedToken}` : null);
    
    if (token) {
      config.headers['Authorization'] = token;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Resume endpoints
export const resumeAPI = {
  uploadResume: (file, jobDescription) => {
    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription) {
      formData.append('job_description', jobDescription);
    }
    return api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  scoreResume: (resumeText, jobDescription) =>
    api.post('/resume/score', {
      resume_text: resumeText,
      job_description: jobDescription,
    }),
  
  extractSkills: (resumeText) =>
    api.post('/resume/extract-skills', {
      resume_text: resumeText,
    }),
  
  getSampleScore: () =>
    api.get('/resume/sample-score'),
};

// Job endpoints
export const jobsAPI = {
  searchJobs: (keyword, location, jobType, source) =>
    api.get('/jobs/search', {
      params: { keyword, location, job_type: jobType, source },
    }),
  
  recommendJobs: (resumeText, topK, location) =>
    api.post('/jobs/recommend', {
      resume_text: resumeText,
      top_k: topK,
      location,
    }),
  
  matchResumeToJob: (resumeText, jobId, jobDescription) =>
    api.post('/jobs/match-resume-to-job', {
      resume_text: resumeText,
      job_id: jobId,
      job_description: jobDescription,
    }),
  
  getTrendingJobs: (limit, location) =>
    api.get('/jobs/trending', {
      params: { limit, location },
    }),
  
  getSkillsDemand: () =>
    api.get('/jobs/skills-demand'),
};

// History endpoints
export const historyAPI = {
  saveAnalysis: (data) =>
    api.post('/history/save', data),
  
  listAnalyses: (skip = 0, limit = 10) =>
    api.get('/history/list', { params: { skip, limit } }),
  
  getLatestAnalysis: () =>
    api.get('/history/latest'),
  
  getAnalysis: (id) =>
    api.get(`/history/${id}`),
  
  deleteAnalysis: (id) =>
    api.delete(`/history/${id}`),
  
  getAnalysisCount: () =>
    api.get('/history/count/total'),
};

// Models endpoints
export const modelsAPI = {
  getStatus: () =>
    api.get('/models/status'),
  
  getPerformance: () =>
    api.get('/models/performance'),
  
  reloadModels: () =>
    api.post('/models/reload'),
};

export default api;
