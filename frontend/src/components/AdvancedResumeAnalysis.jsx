import React, { useState } from 'react';
import { useResumeStore } from '../store';
import {
  FiFileText, FiAward, FiCheckCircle, FiAlertCircle, FiTarget,
  FiTrendingUp, FiZap, FiList, FiStar, FiAlertTriangle, FiInfo,
  FiChevronDown, FiChevronUp
} from 'react-icons/fi';

// Score Circle Component
const ScoreCircle = ({ score, size = 'lg' }) => {
  const percentage = Math.round(score * 100);
  const circumference = 2 * Math.PI * 45;
  const strokeDasharray = `${(percentage / 100) * circumference} ${circumference}`;

  const getColor = (score) => {
    if (score >= 0.8) return { stroke: '#4ade80', text: 'text-green-400', bg: 'bg-green-500/10' };
    if (score >= 0.6) return { stroke: '#facc15', text: 'text-yellow-400', bg: 'bg-yellow-500/10' };
    if (score >= 0.4) return { stroke: '#fb923c', text: 'text-orange-400', bg: 'bg-orange-500/10' };
    return { stroke: '#f87171', text: 'text-red-400', bg: 'bg-red-500/10' };
  };

  const colors = getColor(score);
  const sizeClass = size === 'lg' ? 'w-32 h-32' : 'w-20 h-20';
  const textSize = size === 'lg' ? 'text-3xl' : 'text-lg';

  return (
    <div className={`${sizeClass} relative`}>
      <svg className="w-full h-full transform -rotate-90">
        <circle cx="50%" cy="50%" r="45%" fill="none" stroke="#334155" strokeWidth="8" />
        <circle
          cx="50%" cy="50%" r="45%" fill="none"
          stroke={colors.stroke} strokeWidth="8"
          strokeDasharray={strokeDasharray}
          strokeLinecap="round"
          className="transition-all duration-1000"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`${textSize} font-bold ${colors.text}`}>{percentage}%</span>
      </div>
    </div>
  );
};

// Grade Badge Component
const GradeBadge = ({ grade }) => {
  const gradeColors = {
    'A+': 'bg-green-500', 'A': 'bg-green-500', 'A-': 'bg-green-600',
    'B+': 'bg-blue-500', 'B': 'bg-blue-500', 'B-': 'bg-blue-600',
    'C+': 'bg-yellow-500', 'C': 'bg-yellow-500', 'C-': 'bg-yellow-600',
    'D': 'bg-orange-500', 'F': 'bg-red-500'
  };

  return (
    <span className={`${gradeColors[grade] || 'bg-slate-500'} text-white px-4 py-2 rounded-lg font-bold text-xl shadow-[0_0_15px_rgba(0,0,0,0.3)]`}>
      Grade: {grade}
    </span>
  );
};

// Collapsible Section Component
const CollapsibleSection = ({ title, icon: Icon, children, defaultOpen = true, count }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="glass-card rounded-lg shadow-sm border border-white/5 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between bg-white/5 hover:bg-white/10 transition"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5 text-blue-400" />
          <span className="font-semibold text-slate-200">{title}</span>
          {count !== undefined && (
            <span className="bg-blue-500/20 text-blue-300 text-xs px-2 py-1 rounded-full border border-blue-500/30">
              {count}
            </span>
          )}
        </div>
        {isOpen ? <FiChevronUp className="text-slate-400" /> : <FiChevronDown className="text-slate-400" />}
      </button>
      {isOpen && <div className="p-6">{children}</div>}
    </div>
  );
};

// Progress Bar Component
const ProgressBar = ({ label, value, color = 'blue' }) => {
  const percentage = Math.round(value * 100);
  const colorClasses = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    yellow: 'bg-yellow-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500'
  };

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-slate-400">{label}</span>
        <span className="font-medium text-slate-200">{percentage}%</span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Action Item Component
const ActionItem = ({ item }) => {
  const priorityColors = {
    high: 'border-red-500 bg-red-500/10',
    medium: 'border-yellow-500 bg-yellow-500/10',
    low: 'border-green-500 bg-green-500/10'
  };

  const priorityIcons = {
    high: <FiAlertCircle className="text-red-500" />,
    medium: <FiAlertTriangle className="text-yellow-500" />,
    low: <FiInfo className="text-green-500" />
  };

  return (
    <div className={`border-l-4 ${priorityColors[item.priority]} p-4 rounded-r-lg`}>
      <div className="flex items-start gap-3">
        <div className="mt-1">{priorityIcons[item.priority]}</div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-200">{item.category}</span>
            <span className={`text-xs px-2 py-0.5 rounded ${item.priority === 'high' ? 'bg-red-500/20 text-red-300' :
              item.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                'bg-green-500/20 text-green-300'
              }`}>
              {item.priority.toUpperCase()}
            </span>
          </div>
          <p className="text-slate-300 mt-1">{item.action}</p>
          <p className="text-sm text-slate-500 mt-1">{item.impact}</p>
        </div>
      </div>
    </div>
  );
};

// Skill Badge Component
const SkillBadge = ({ skill, type }) => {
  const styles = {
    matched: 'bg-green-500/10 text-green-400 border border-green-500/20',
    missing: 'bg-red-500/10 text-red-400 border border-red-500/20',
    extra: 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
  };

  return (
    <span className={`${styles[type]} px-3 py-1 rounded-full text-sm font-medium`}>
      {skill}
      {type === 'matched' && <FiCheckCircle className="inline ml-1 w-3 h-3" />}
      {type === 'missing' && <FiAlertCircle className="inline ml-1 w-3 h-3" />}
    </span>
  );
};

// Main Component
export const AdvancedResumeAnalysis = () => {
  const { atsAnalysis, extractedInfo } = useResumeStore();

  // If we only have extracted info (no job description provided)
  if (!atsAnalysis && extractedInfo) {
    return (
      <div className="space-y-6">
        <div className="bg-blue-500/10 border border-blue-500/20 p-6 rounded-lg">
          <div className="flex items-center gap-3 mb-4">
            <FiInfo className="w-6 h-6 text-blue-400" />
            <h3 className="text-lg font-semibold text-blue-300">Resume Scanned Successfully</h3>
          </div>
          <p className="text-blue-200">
            Add a job description to get your personalized ATS score and detailed recommendations.
          </p>
        </div>

        <CollapsibleSection title="Extracted Skills" icon={FiTarget} count={extractedInfo.skills?.length}>
          <div className="flex flex-wrap gap-2">
            {extractedInfo.skills?.map((skill, idx) => (
              <span key={idx} className="bg-blue-500/10 text-blue-300 px-3 py-1 rounded-full text-sm border border-blue-500/20">
                {skill}
              </span>
            ))}
          </div>
        </CollapsibleSection>

        {extractedInfo.contact_info && Object.keys(extractedInfo.contact_info).length > 0 && (
          <CollapsibleSection title="Contact Information" icon={FiFileText}>
            <div className="grid grid-cols-2 gap-4">
              {extractedInfo.contact_info.email && (
                <div>
                  <p className="text-sm text-slate-500">Email</p>
                  <p className="font-medium text-slate-200">{extractedInfo.contact_info.email}</p>
                </div>
              )}
              {extractedInfo.contact_info.phone && (
                <div>
                  <p className="text-sm text-slate-500">Phone</p>
                  <p className="font-medium text-slate-200">{extractedInfo.contact_info.phone}</p>
                </div>
              )}
            </div>
          </CollapsibleSection>
        )}
      </div>
    );
  }

  if (!atsAnalysis) {
    return (
      <div className="glass-card p-8 rounded-lg shadow text-center border-none">
        <FiFileText className="w-16 h-16 mx-auto text-slate-600 mb-4" />
        <p className="text-slate-400">Upload a resume to see comprehensive ATS analysis</p>
      </div>
    );
  }

  const {
    overall_score,
    grade,
    method,
    score_breakdown,
    skills_analysis,
    format_analysis,
    extracted_info,
    detailed_analysis,
    ai_recommendations,
    action_items,
    score_explanation
  } = atsAnalysis;

  return (
    <div className="space-y-6">
      {/* Main Score Card */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-center md:text-left">
            <h2 className="text-2xl font-bold mb-2">ATS Compatibility Score</h2>
            <p className="text-blue-100 mb-4">
              Powered by {method === 'neural_network' ? 'Neural Network AI' :
                method === 'gradient_boosting' ? 'Gradient Boosting ML' :
                  method === 'random_forest' ? 'Random Forest ML' : 'Advanced Analysis'}
            </p>
            <GradeBadge grade={grade} />
          </div>
          <ScoreCircle score={overall_score} size="lg" />
        </div>

        {/* Score Explanation */}
        <div className="mt-6 p-4 bg-white/10 rounded-lg">
          <p className="text-blue-50">{score_explanation}</p>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="glass-card rounded-xl shadow-sm p-6 border-none">
        <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-white">
          <FiTrendingUp className="text-blue-400" />
          Score Breakdown
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ProgressBar label="Skill Match" value={score_breakdown?.skill_match || 0} color="green" />
          <ProgressBar label="Keyword Match" value={score_breakdown?.keyword_match || 0} color="blue" />
          <ProgressBar label="Format Score" value={score_breakdown?.format_score || 0} color="purple" />
          <ProgressBar label="Content Similarity" value={score_breakdown?.content_similarity || 0} color="orange" />
          {score_breakdown?.ml_prediction && (
            <div className="md:col-span-2">
              <ProgressBar label="ML Prediction" value={score_breakdown.ml_prediction} color="blue" />
            </div>
          )}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      {detailed_analysis && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strengths */}
          <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-green-400">
              <FiCheckCircle />
              Strengths
            </h3>
            <ul className="space-y-3">
              {detailed_analysis.strengths?.map((strength, idx) => (
                <li key={idx} className="flex items-start gap-2 text-green-300">
                  <FiCheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>{strength}</span>
                </li>
              ))}
              {(!detailed_analysis.strengths || detailed_analysis.strengths.length === 0) && (
                <li className="text-green-400">Add more relevant content to highlight strengths</li>
              )}
            </ul>
          </div>

          {/* Weaknesses */}
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-red-400">
              <FiAlertCircle />
              Areas to Improve
            </h3>
            <ul className="space-y-3">
              {detailed_analysis.weaknesses?.map((weakness, idx) => (
                <li key={idx} className="flex items-start gap-2 text-red-300">
                  <FiAlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>{weakness}</span>
                </li>
              ))}
              {(!detailed_analysis.weaknesses || detailed_analysis.weaknesses.length === 0) && (
                <li className="text-red-400">Great job! No major weaknesses found.</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* AI Recommendations */}
      {ai_recommendations && ai_recommendations.length > 0 && (
        <CollapsibleSection title="AI-Powered Recommendations" icon={FiZap} count={ai_recommendations.length}>
          <div className="space-y-4">
            {ai_recommendations.map((rec, idx) => (
              <div key={idx} className="flex items-start gap-4 p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0 shadow-lg">
                  {idx + 1}
                </div>
                <p className="text-slate-300">{rec}</p>
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* Action Items */}
      {action_items && action_items.length > 0 && (
        <CollapsibleSection title="Priority Action Items" icon={FiList} count={action_items.length}>
          <div className="space-y-4">
            {action_items.map((item, idx) => (
              <ActionItem key={idx} item={item} />
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* Skills Analysis */}
      {skills_analysis && (
        <CollapsibleSection
          title="Skills Analysis"
          icon={FiTarget}
          count={`${skills_analysis.matched_skills?.length || 0}/${(skills_analysis.matched_skills?.length || 0) + (skills_analysis.missing_skills?.length || 0)}`}
        >
          <div className="space-y-6">
            {/* Matched Skills */}
            {skills_analysis.matched_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold text-green-400 mb-3 flex items-center gap-2">
                  <FiCheckCircle /> Matched Skills ({skills_analysis.matched_skills.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {skills_analysis.matched_skills.map((skill, idx) => (
                    <SkillBadge key={idx} skill={skill} type="matched" />
                  ))}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            {skills_analysis.missing_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold text-red-400 mb-3 flex items-center gap-2">
                  <FiAlertCircle /> Missing Skills ({skills_analysis.missing_skills.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {skills_analysis.missing_skills.map((skill, idx) => (
                    <SkillBadge key={idx} skill={skill} type="missing" />
                  ))}
                </div>
              </div>
            )}

            {/* Extra Skills */}
            {skills_analysis.extra_skills?.length > 0 && (
              <div>
                <h4 className="font-semibold text-blue-400 mb-3 flex items-center gap-2">
                  <FiStar /> Additional Skills ({skills_analysis.extra_skills.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {skills_analysis.extra_skills.slice(0, 15).map((skill, idx) => (
                    <SkillBadge key={idx} skill={skill} type="extra" />
                  ))}
                </div>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* Format Analysis */}
      {format_analysis && (
        <CollapsibleSection title="Format & Structure Analysis" icon={FiFileText} defaultOpen={false}>
          <div className="space-y-6">
            {/* Sections Found */}
            <div>
              <h4 className="font-semibold mb-3 text-slate-300">Resume Sections Detected</h4>
              <div className="flex flex-wrap gap-2">
                {format_analysis.sections_found?.map((section, idx) => (
                  <span key={idx} className="bg-blue-500/10 text-blue-300 px-3 py-1 rounded-full text-sm border border-blue-500/20">
                    {section}
                  </span>
                ))}
              </div>
            </div>

            {/* Action Verbs */}
            <div>
              <h4 className="font-semibold mb-3 text-slate-300">
                Action Verbs Used ({format_analysis.action_verbs_count || 0})
              </h4>
              <div className="flex flex-wrap gap-2">
                {format_analysis.action_verbs_used?.map((verb, idx) => (
                  <span key={idx} className="bg-green-500/10 text-green-300 px-3 py-1 rounded-full text-sm capitalize border border-green-500/20">
                    {verb}
                  </span>
                ))}
              </div>
            </div>

            {/* Format Issues */}
            {format_analysis.format_issues?.length > 0 && (
              <div>
                <h4 className="font-semibold text-orange-400 mb-3">Format Issues</h4>
                <ul className="space-y-2">
                  {format_analysis.format_issues.map((issue, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-orange-300">
                      <FiAlertTriangle className="w-4 h-4 flex-shrink-0" />
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Format Suggestions */}
            {format_analysis.format_suggestions?.length > 0 && (
              <div>
                <h4 className="font-semibold text-blue-400 mb-3">Suggestions</h4>
                <ul className="space-y-2">
                  {format_analysis.format_suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-blue-300">
                      <FiInfo className="w-4 h-4 flex-shrink-0" />
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* Extracted Information */}
      {extracted_info && (
        <CollapsibleSection title="Extracted Information" icon={FiAward} defaultOpen={false}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-purple-500/10 p-4 rounded-lg text-center border border-purple-500/20">
              <p className="text-sm text-slate-400">Experience</p>
              <p className="text-3xl font-bold text-purple-400">{extracted_info.experience_years || 0}+</p>
              <p className="text-sm text-slate-500">Years</p>
            </div>
            <div className="bg-blue-500/10 p-4 rounded-lg text-center border border-blue-500/20">
              <p className="text-sm text-slate-400">Total Skills</p>
              <p className="text-3xl font-bold text-blue-400">{extracted_info.total_skills_found || 0}</p>
              <p className="text-sm text-slate-500">Detected</p>
            </div>
          </div>

          {extracted_info.contact_info && Object.keys(extracted_info.contact_info).length > 0 && (
            <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <h4 className="font-semibold mb-3 text-slate-300">Contact Information</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                {extracted_info.contact_info.email && (
                  <div className="text-slate-200"><span className="text-slate-500">Email:</span> {extracted_info.contact_info.email}</div>
                )}
                {extracted_info.contact_info.phone && (
                  <div className="text-slate-200"><span className="text-slate-500">Phone:</span> {extracted_info.contact_info.phone}</div>
                )}
                {extracted_info.contact_info.linkedin && (
                  <div className="text-slate-200"><span className="text-slate-500">LinkedIn:</span> {extracted_info.contact_info.linkedin}</div>
                )}
                {extracted_info.contact_info.github && (
                  <div className="text-slate-200"><span className="text-slate-500">GitHub:</span> {extracted_info.contact_info.github}</div>
                )}
              </div>
            </div>
          )}
        </CollapsibleSection>
      )}
    </div>
  );
};

export default AdvancedResumeAnalysis;
