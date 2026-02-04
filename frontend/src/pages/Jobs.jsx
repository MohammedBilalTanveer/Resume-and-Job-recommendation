import React from 'react';
import { JobRecommendations } from '../components/JobRecommendations';
import { SkillsDemand } from '../components/SkillsDemand';

export const Jobs = () => {
  return (
    <div className="space-y-8">
      <JobRecommendations />
      <SkillsDemand />
    </div>
  );
};
