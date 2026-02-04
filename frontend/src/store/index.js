import { create } from 'zustand';

export const useResumeStore = create((set) => ({
  resume: null,
  resumeText: '',
  atsAnalysis: null,
  extractedInfo: null,
  loading: false,
  error: null,
  
  setResume: (resume) => set({ resume }),
  setResumeText: (text) => set({ resumeText: text }),
  setAtsAnalysis: (analysis) => set({ atsAnalysis: analysis }),
  setExtractedInfo: (info) => set({ extractedInfo: info }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  reset: () => set({
    resume: null,
    resumeText: '',
    atsAnalysis: null,
    extractedInfo: null,
    loading: false,
    error: null,
  }),
}));

export const useJobStore = create((set) => ({
  jobs: [],
  recommendations: [],
  selectedJob: null,
  loading: false,
  error: null,
  
  setJobs: (jobs) => set({ jobs }),
  setRecommendations: (recs) => set({ recommendations: recs }),
  setSelectedJob: (job) => set({ selectedJob: job }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  reset: () => set({
    jobs: [],
    recommendations: [],
    selectedJob: null,
    loading: false,
    error: null,
  }),
}));
