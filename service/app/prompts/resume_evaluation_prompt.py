
def build_resume_evaluation_prompt(resume_text: str, job_description: str) -> str:
    prompt = f"""
You are an expert resume analyst and ATS optimization assistant.  
Your task is to evaluate a candidate's resume against a job description and produce a structured JSON response that EXACTLY matches the Pydantic model schema provided below.

STRICT REQUIREMENTS:
- You MUST return ONLY valid JSON.
- The JSON MUST strictly follow the structure and field types of the schema.
- Do NOT include any explanatory text before or after the JSON.
- All lists must be present (empty lists are allowed).
- Every field in the schema must be included.

Pydantic Schema (for reference only):

ResumeEvaluationResult {{
    ats_score: int
    summary: str
    missing_keywords: List[str]
    skills_match: SkillsMatch {{
        matched_skills: List[str]
        unmatched_skills: List[str]
    }}
    section_feedback: List[SectionFeedbackItem] {{
        section: str
        issues: List[str]
    }}
    line_by_line_suggestions: List[LineSuggestion] {{
        original_text: str
        suggested_improvement: str
        reason: str
    }}
    recommended_new_bullets: List[RecommendedBullet] {{
        job_responsibility_from_jd: str
        suggested_bullet: str
        importance: str
    }}
}}

-------------------------------------
INPUT:
RESUME TEXT:
{resume_text}

JOB DESCRIPTION TEXT:
{job_description}

-------------------------------------
TASKS:

1. Extract key skills, responsibilities, and required technologies from the Job Description.
2. Compare them with the resume to determine:
   - Matches
   - Missing skills / gaps
3. Evaluate the resume for:
   - Clarity
   - Impact
   - Quantifiable achievements
   - Relevance to the JD
4. Compute an ATS relevance score from 0 to 100.
5. Provide:
   - High-level summary feedback
   - Section-wise issues
   - A list of specific line-by-line improvement suggestions:
        • include the ORIGINAL resume line  
        • include the IMPROVED suggested version  
        • include the REASON for the improvement
6. Generate NEW recommended bullet points to cover missing responsibilities from the JD.
   Each bullet must include:
        - JD responsibility
        - Suggested new bullet
        - Importance level ("high", "medium", or "low")

-------------------------------------
OUTPUT:
Return ONLY valid JSON matching the ResumeEvaluationResult schema exactly.
"""
    return prompt.strip()
