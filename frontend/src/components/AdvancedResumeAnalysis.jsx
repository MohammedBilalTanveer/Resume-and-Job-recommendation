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
    if (score >= 0.8) return { stroke: '#22c55e', text: 'text-green-500', bg: 'bg-green-50' };
    if (score >= 0.6) return { stroke: '#eab308', text: 'text-yellow-500', bg: 'bg-yellow-50' };
    if (score >= 0.4) return { stroke: '#f97316', text: 'text-orange-500', bg: 'bg-orange-50' };
    return { stroke: '#ef4444', text: 'text-red-500', bg: 'bg-red-50' };
  };
  
  const colors = getColor(score);
  const sizeClass = size === 'lg' ? 'w-32 h-32' : 'w-20 h-20';
  const textSize = size === 'lg' ? 'text-3xl' : 'text-lg';
  
  return (
    <div className={`${sizeClass} relative`}>
      <svg className="w-full h-full transform -rotate-90">
        <circle cx="50%" cy="50%" r="45%" fill="none" stroke="#e5e7eb" strokeWidth="8"/>
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
    'A+': 'bg-green-500', 'A': 'bg-green-500', 'A-': 'bg-green-400',
    'B+': 'bg-blue-500', 'B': 'bg-blue-500', 'B-': 'bg-blue-400',
    'C+': 'bg-yellow-500', 'C': 'bg-yellow-500', 'C-': 'bg-yellow-400',
    'D': 'bg-orange-500', 'F': 'bg-red-500'
  };
  
  return (
    <span className={`${gradeColors[grade] || 'bg-gray-500'} text-white px-4 py-2 rounded-lg font-bold text-xl`}>
      Grade: {grade}
    </span>
  );
};

// Collapsible Section Component
const CollapsibleSection = ({ title, icon: Icon, children, defaultOpen = true, count }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5 text-blue-600" />
          <span className="font-semibold text-gray-800">{title}</span>
          {count !== undefined && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {count}
            </span>
          )}
        </div>
        {isOpen ? <FiChevronUp /> : <FiChevronDown />}
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
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{percentage}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
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
    high: 'border-red-500 bg-red-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-green-500 bg-green-50'
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
            <span className="font-semibold text-gray-800">{item.category}</span>
            <span className={`text-xs px-2 py-0.5 rounded ${
              item.priority === 'high' ? 'bg-red-200 text-red-800' :
              item.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
              'bg-green-200 text-green-800'
            }`}>
              {item.priority.toUpperCase()}
            </span>
          </div>
          <p className="text-gray-700 mt-1">{item.action}</p>
          <p className="text-sm text-gray-500 mt-1">{item.impact}</p>
        </div>
      </div>
    </div>
  );
};

// Skill Badge Component
const SkillBadge = ({ skill, type }) => {
  const styles = {
    matched: 'bg-green-100 text-green-800 border border-green-200',
    missing: 'bg-red-100 text-red-800 border border-red-200',
    extra: 'bg-blue-100 text-blue-800 border border-blue-200'
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
        <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
          <div className="flex items-center gap-3 mb-4">
            <FiInfo className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-blue-800">Resume Scanned Successfully</h3>
          </div>
          <p className="text-blue-700">
            Add a job description to get your personalized ATS score and detailed recommendations.
          </p>
        </div>
        
        <CollapsibleSection title="Extracted Skills" icon={FiTarget} count={extractedInfo.skills?.length}>
          <div className="flex flex-wrap gap-2">
            {extractedInfo.skills?.map((skill, idx) => (
              <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
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
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="font-medium">{extractedInfo.contact_info.email}</p>
                </div>
              )}
              {extractedInfo.contact_info.phone && (
                <div>
                  <p className="text-sm text-gray-500">Phone</p>
                  <p className="font-medium">{extractedInfo.contact_info.phone}</p>
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
      <div className="bg-white p-8 rounded-lg shadow text-center">
        <FiFileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <p className="text-gray-600">Upload a resume to see comprehensive ATS analysis</p>
      </div>
    );
  }
  
  const {
    overall_score,
    score_percentage,
    grade,
    method,
    score_breakdown,
    skills_analysis,
    keyword_analysis,
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
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
          <FiTrendingUp className="text-blue-600" />
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
          <div className="bg-green-50 border border-green-200 rounded-xl p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-green-800">
              <FiCheckCircle />
              Strengths
            </h3>
            <ul className="space-y-3">
              {detailed_analysis.strengths?.map((strength, idx) => (
                <li key={idx} className="flex items-start gap-2 text-green-700">
                  <FiCheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>{strength}</span>
                </li>
              ))}
              {(!detailed_analysis.strengths || detailed_analysis.strengths.length === 0) && (
                <li className="text-green-600">Add more relevant content to highlight strengths</li>
              )}
            </ul>
          </div>
          
          {/* Weaknesses */}
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-red-800">
              <FiAlertCircle />
              Areas to Improve
            </h3>
            <ul className="space-y-3">
              {detailed_analysis.weaknesses?.map((weakness, idx) => (
                <li key={idx} className="flex items-start gap-2 text-red-700">
                  <FiAlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>{weakness}</span>
                </li>
              ))}
              {(!detailed_analysis.weaknesses || detailed_analysis.weaknesses.length === 0) && (
                <li className="text-red-600">Great job! No major weaknesses found.</li>
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
              <div key={idx} className="flex items-start gap-4 p-4 bg-purple-50 border border-purple-100 rounded-lg">
                <div className="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  {idx + 1}
                </div>
                <p className="text-gray-700">{rec}</p>
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
                <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
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
                <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
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
                <h4 className="font-semibold text-blue-700 mb-3 flex items-center gap-2">
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
              <h4 className="font-semibold mb-3">Resume Sections Detected</h4>
              <div className="flex flex-wrap gap-2">
                {format_analysis.sections_found?.map((section, idx) => (
                  <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                    {section}
                  </span>
                ))}
              </div>
            </div>
            
            {/* Action Verbs */}
            <div>
              <h4 className="font-semibold mb-3">
                Action Verbs Used ({format_analysis.action_verbs_count || 0})
              </h4>
              <div className="flex flex-wrap gap-2">
                {format_analysis.action_verbs_used?.map((verb, idx) => (
                  <span key={idx} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm capitalize">
                    {verb}
                  </span>
                ))}
              </div>
            </div>
            
            {/* Format Issues */}
            {format_analysis.format_issues?.length > 0 && (
              <div>
                <h4 className="font-semibold text-orange-700 mb-3">Format Issues</h4>
                <ul className="space-y-2">
                  {format_analysis.format_issues.map((issue, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-orange-700">
                      <FiAlertTriangle className="w-4 h-4" />
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Format Suggestions */}
            {format_analysis.format_suggestions?.length > 0 && (
              <div>
                <h4 className="font-semibold text-blue-700 mb-3">Suggestions</h4>
                <ul className="space-y-2">
                  {format_analysis.format_suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-blue-700">
                      <FiInfo className="w-4 h-4" />
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
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <p className="text-sm text-gray-600">Experience</p>
              <p className="text-3xl font-bold text-purple-600">{extracted_info.experience_years || 0}+</p>
              <p className="text-sm text-gray-500">Years</p>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <p className="text-sm text-gray-600">Total Skills</p>
              <p className="text-3xl font-bold text-blue-600">{extracted_info.total_skills_found || 0}</p>
              <p className="text-sm text-gray-500">Detected</p>
            </div>
          </div>
          
          {extracted_info.contact_info && Object.keys(extracted_info.contact_info).length > 0 && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-3">Contact Information</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                {extracted_info.contact_info.email && (
                  <div><span className="text-gray-500">Email:</span> {extracted_info.contact_info.email}</div>
                )}
                {extracted_info.contact_info.phone && (
                  <div><span className="text-gray-500">Phone:</span> {extracted_info.contact_info.phone}</div>
                )}
                {extracted_info.contact_info.linkedin && (
                  <div><span className="text-gray-500">LinkedIn:</span> {extracted_info.contact_info.linkedin}</div>
                )}
                {extracted_info.contact_info.github && (
                  <div><span className="text-gray-500">GitHub:</span> {extracted_info.contact_info.github}</div>
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
