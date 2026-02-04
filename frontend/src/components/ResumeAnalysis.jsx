import React, { useState, useEffect } from 'react';
import { useResumeStore } from '../store';
import { ATSScoreDisplay, KeywordBadge, ScoreBreakdown } from './Common';
import { FiFileText, FiAward, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';

export const ResumeAnalysis = () => {
  const { resumeText, extractedData, atsScore, matchingKeywords, missingKeywords, scoreBreakdown, method } = useResumeStore();

  if (!extractedData) {
    return (
      <div className="bg-white p-8 rounded-lg shadow text-center">
        <p className="text-gray-600">Upload a resume to see analysis</p>
      </div>
    );
  }

  const skills = extractedData.skills || [];
  const experience = extractedData.experience_years || 0;
  const education = extractedData.education || [];
  const contact = extractedData.contact_info || {};

  return (
    <div className="space-y-6">
      {/* ATS Score */}
      {atsScore !== null && (
        <>
          <ATSScoreDisplay score={atsScore} />
          
          {/* Method Used */}
          {method && (
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-700">
                <strong>Scoring Method:</strong> {method === 'neural_network' ? 'Neural Network (AI-Powered)' : method === 'gradient_boosting' ? 'Gradient Boosting' : method === 'random_forest' ? 'Random Forest' : 'Rule-Based'}
              </p>
            </div>
          )}
          
          {/* Score Breakdown */}
          {scoreBreakdown && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Score Breakdown</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {scoreBreakdown.ml_model_score !== null && (
                  <div className="bg-blue-50 p-4 rounded">
                    <p className="text-sm text-gray-600">ML Model Score</p>
                    <p className="text-2xl font-bold text-blue-600">{(scoreBreakdown.ml_model_score * 100).toFixed(1)}%</p>
                  </div>
                )}
                {scoreBreakdown.skill_match !== null && (
                  <div className="bg-green-50 p-4 rounded">
                    <p className="text-sm text-gray-600">Skill Match</p>
                    <p className="text-2xl font-bold text-green-600">{(scoreBreakdown.skill_match * 100).toFixed(1)}%</p>
                  </div>
                )}
                {scoreBreakdown.keyword_score !== null && (
                  <div className="bg-purple-50 p-4 rounded">
                    <p className="text-sm text-gray-600">Keyword Match</p>
                    <p className="text-2xl font-bold text-purple-600">{(scoreBreakdown.keyword_score * 100).toFixed(1)}%</p>
                  </div>
                )}
                {scoreBreakdown.content_similarity !== null && (
                  <div className="bg-orange-50 p-4 rounded">
                    <p className="text-sm text-gray-600">Content Match</p>
                    <p className="text-2xl font-bold text-orange-600">{(scoreBreakdown.content_similarity * 100).toFixed(1)}%</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Contact Info */}
      {Object.keys(contact).length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <FiFileText className="w-5 h-5 text-blue-600" />
            Contact Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {contact.email && (
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{contact.email}</p>
              </div>
            )}
            {contact.phone && (
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium">{contact.phone}</p>
              </div>
            )}
            {contact.linkedin && (
              <div>
                <p className="text-sm text-gray-600">LinkedIn</p>
                <p className="font-medium truncate">{contact.linkedin}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Experience & Education */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <FiAward className="w-5 h-5 text-purple-600" />
            Experience
          </h3>
          <p className="text-2xl font-bold text-purple-600">{experience}+</p>
          <p className="text-sm text-gray-600">Years</p>
        </div>

        {education.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-bold mb-4">Education</h3>
            <div className="space-y-2">
              {education.map((edu, idx) => (
                <p key={idx} className="text-sm text-gray-700">
                  • {edu}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Skills */}
      {skills.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <FiCheckCircle className="w-5 h-5 text-green-600" />
            Extracted Skills ({skills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, idx) => (
              <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Matching & Missing Keywords */}
      {(matchingKeywords.length > 0 || missingKeywords.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {matchingKeywords.length > 0 && (
            <div className="bg-green-50 p-6 rounded-lg border border-green-200">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-green-700">
                <FiCheckCircle className="w-5 h-5" />
                Matching Keywords
              </h3>
              <div className="flex flex-wrap gap-2">
                {matchingKeywords.map((keyword, idx) => (
                  <KeywordBadge key={idx} keyword={keyword} isMissing={false} />
                ))}
              </div>
            </div>
          )}

          {missingKeywords.length > 0 && (
            <div className="bg-red-50 p-6 rounded-lg border border-red-200">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-red-700">
                <FiAlertCircle className="w-5 h-5" />
                Missing Keywords
              </h3>
              <div className="flex flex-wrap gap-2">
                {missingKeywords.map((keyword, idx) => (
                  <KeywordBadge key={idx} keyword={keyword} isMissing={true} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
