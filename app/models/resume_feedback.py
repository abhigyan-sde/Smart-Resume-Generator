from typing import List, Optional
from pydantic import BaseModel


class SkillsMatch(BaseModel):
    matched_skills: List[str]
    unmatched_skills: List[str]


class SectionFeedbackItem(BaseModel):
    section: str
    issues: List[str]


class LineSuggestion(BaseModel):
    original_text: str
    suggested_improvement: str
    reason: str


class RecommendedBullet(BaseModel):
    job_responsibility_from_jd: str
    suggested_bullet: str
    importance: str  # "high" | "medium" | "low"


class ResumeEvaluationResult(BaseModel):
    ats_score: int
    summary: str
    missing_keywords: List[str]
    skills_match: SkillsMatch
    section_feedback: List[SectionFeedbackItem]
    line_by_line_suggestions: List[LineSuggestion]
    recommended_new_bullets: List[RecommendedBullet]
