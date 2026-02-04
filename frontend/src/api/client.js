import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
