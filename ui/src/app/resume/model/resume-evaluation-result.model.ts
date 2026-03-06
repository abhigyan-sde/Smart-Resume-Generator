export interface SkillsMatch {
  matched_skills: string[];
  unmatched_skills: string[];
}

export interface SectionFeedbackItem {
  section: string;
  issues: string[];
}

export interface LineSuggestion {
  lineId?: number | null;
  original_text: string;
  suggested_improvement: string;
  reason: string;
  edited_suggestion?: string;
  isApplied?: boolean;
}

export interface RecommendedBullet {
  job_responsibility_from_jd: string;
  suggested_bullet: string;
  importance: string;
}

export interface ResumeEvaluationResult {
  ats_score: number;
  summary: string;
  missing_keywords: string[];
  skills_match: SkillsMatch;
  section_feedback: SectionFeedbackItem[];
  line_by_line_suggestions: LineSuggestion[];
  recommended_new_bullets: RecommendedBullet[];
}
