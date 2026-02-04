import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiUpload, FiTarget, FiTrendingUp } from 'react-icons/fi';

export const Home = () => {
  const features = [
    {
      icon: FiUpload,
      title: 'Resume Upload',
      description: 'Upload your resume in PDF format for instant analysis'
    },
    {
      icon: FiTarget,
      title: 'ATS Scoring',
      description: 'Get AI-powered ATS scores to optimize your resume'
    },
    {
      icon: FiTrendingUp,
      title: 'Job Matching',
      description: 'Find jobs that match your skills and experience'
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-12 rounded-lg">
        <h1 className="text-4xl font-bold mb-4">
          Your AI-Powered Resume & Job Matching Platform
        </h1>
        <p className="text-xl mb-8 opacity-90">
          Upload your resume, get an ATS score, and discover jobs that match your profile
        </p>
        <Link
          to="/analyzer"
          className="inline-flex items-center gap-2 bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
        >
          Get Started <FiArrowRight />
        </Link>
      </div>

      {/* Features */}
      <div>
        <h2 className="text-3xl font-bold mb-8">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, description }, idx) => (
            <div key={idx} className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
              <Icon className="w-10 h-10 text-blue-600 mb-4" />
              <h3 className="text-lg font-bold mb-2">{title}</h3>
              <p className="text-gray-600">{description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gray-50 p-8 rounded-lg">
        <h2 className="text-3xl font-bold mb-8">How It Works</h2>
        <div className="space-y-4">
          {[
            '1. Upload your resume in PDF format',
            '2. Our AI analyzes your resume and extracts skills',
            '3. Get your ATS score and optimization suggestions',
            '4. Browse and apply to matching jobs',
          ].map((step, idx) => (
            <div key={idx} className="flex items-center gap-4">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                {idx + 1}
              </div>
              <p className="text-gray-700">{step}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="bg-blue-50 border-2 border-blue-200 p-8 rounded-lg text-center">
        <h2 className="text-2xl font-bold mb-4">Ready to Optimize Your Resume?</h2>
        <Link
          to="/analyzer"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          Start Analyzing
        </Link>
      </div>
    </div>
  );
};
