import React, { useState } from 'react';
import { resumeAPI } from '../api/client';
import { useResumeStore } from '../store';
import { LoadingSpinner } from './Common';
import { FiUploadCloud, FiX, FiFileText, FiCheckCircle } from 'react-icons/fi';

export const ResumeUpload = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  
  const { setResume, setResumeText, setAtsAnalysis, setExtractedInfo, reset } = useResumeStore();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const validExtensions = ['.pdf', '.txt', '.docx'];
      const fileExtension = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
      
      if (validTypes.includes(selectedFile.type) || validExtensions.includes(fileExtension)) {
        setFile(selectedFile);
        setError(null);
        setUploadSuccess(false);
      } else {
        setError('Please select a PDF, TXT, or DOCX file');
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    reset(); // Clear previous data

    try {
      const response = await resumeAPI.uploadResume(file, jobDescription);
      const data = response.data;

      setResume(file);
      setResumeText(data.resume_text);
      
      // Handle comprehensive analysis response
      if (data.ats_analysis) {
        setAtsAnalysis(data.ats_analysis);
        setExtractedInfo(null);
      } else if (data.extracted_info) {
        setExtractedInfo(data.extracted_info);
        setAtsAnalysis(null);
      }
      
      setUploadSuccess(true);
      onSuccess?.(data);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setJobDescription('');
    setUploadSuccess(false);
    setError(null);
    reset();
  };

  return (
    <form onSubmit={handleUpload} className="bg-white p-8 rounded-xl shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Upload Your Resume</h2>
        {uploadSuccess && (
          <button
            type="button"
            onClick={handleReset}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Upload New Resume
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* File Upload */}
        <div className={`border-2 border-dashed rounded-xl p-8 text-center transition ${
          uploadSuccess ? 'border-green-300 bg-green-50' : 'border-blue-300 hover:bg-blue-50'
        }`}>
          {uploadSuccess ? (
            <div className="flex flex-col items-center">
              <FiCheckCircle className="w-12 h-12 text-green-500 mb-3" />
              <p className="text-green-700 font-semibold">{file?.name}</p>
              <p className="text-sm text-green-600 mt-1">Resume uploaded successfully!</p>
            </div>
          ) : (
            <>
              <FiUploadCloud className="w-12 h-12 mx-auto text-blue-500 mb-3" />
              <label className="block cursor-pointer">
                <span className="text-blue-600 font-semibold hover:underline">
                  Click to select a file
                </span>
                <p className="text-sm text-gray-500 mt-1">Supports PDF, DOCX, TXT</p>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                  disabled={loading}
                />
              </label>
              {file && (
                <div className="mt-4 flex items-center justify-center gap-2 bg-white px-4 py-2 rounded-lg">
                  <FiFileText className="text-blue-500" />
                  <span className="text-sm text-gray-700">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="text-red-500 hover:text-red-700 ml-2"
                  >
                    <FiX />
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Job Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Description
            <span className="text-gray-400 font-normal ml-1">(Required for ATS score)</span>
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here to get your ATS compatibility score, detailed analysis, and personalized recommendations..."
            rows="6"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1">
            Include the full job posting for best results - requirements, responsibilities, and qualifications.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <FiX className="w-5 h-5" />
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!file || loading}
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
        >
          {loading ? (
            <>
              <LoadingSpinner size="sm" />
              Analyzing Resume...
            </>
          ) : uploadSuccess ? (
            'Re-analyze Resume'
          ) : (
            'Upload & Analyze'
          )}
        </button>

        {/* Help Text */}
        {!uploadSuccess && (
          <p className="text-center text-sm text-gray-500">
            Your resume will be analyzed using AI-powered ATS scoring algorithms
          </p>
        )}
      </div>
    </form>
  );
};
