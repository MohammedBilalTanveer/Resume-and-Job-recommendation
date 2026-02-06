import React from 'react';
import { ResumeUpload } from '../components/ResumeUpload';
import { AdvancedResumeAnalysis } from '../components/AdvancedResumeAnalysis';
import { useResumeStore } from '../store';

export const Analyzer = () => {
  const { atsAnalysis, extractedInfo, resumeText } = useResumeStore();
  const hasData = atsAnalysis || extractedInfo || resumeText;

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          AI-Powered ATS Resume Analyzer
        </h1>
        <p className="text-slate-300">
          Get comprehensive analysis, score breakdown, and personalized recommendations
        </p>
      </div>

      <div className={`grid grid-cols-1 ${hasData ? 'lg:grid-cols-3' : ''} gap-8`}>
        <div className={hasData ? 'lg:col-span-1' : 'max-w-2xl mx-auto w-full'}>
          <ResumeUpload />
        </div>

        {hasData && (
          <div className="lg:col-span-2">
            <AdvancedResumeAnalysis />
          </div>
        )}
      </div>
    </div>
  );
};
