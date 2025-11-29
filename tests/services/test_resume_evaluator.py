import pytest
from unittest.mock import AsyncMock, patch
from app.services.evaluate_resume import evaluate_resume_against_jd
from app.models.resume_feedback import ResumeEvaluationResult

SAMPLE_RESUME_TEXT = """
John Doe
Software Engineer
Developed APIs and improved system performance.
"""

SAMPLE_JD_TEXT = """
We are looking for a Software Engineer with experience in APIs, cloud, CI/CD pipelines.
"""

# Fake JSON returned by LLM
FAKE_LLM_RESPONSE = """
{
  "ats_score": 85,
  "summary": "Strong API experience but missing CI/CD.",
  "missing_keywords": ["CI/CD"],
  "skills_match": {
    "matched_skills": ["APIs"],
    "unmatched_skills": ["CI/CD","cloud"]
  },
  "section_feedback": [
    {
      "section": "Experience",
      "issues": ["Add metrics"]
    }
  ],
  "line_by_line_suggestions": [
    {
      "original_text": "Developed APIs",
      "suggested_improvement": "Developed scalable APIs handling 1000+ requests/min.",
      "reason": "Adds measurable impact."
    }
  ],
  "recommended_new_bullets": [
    {
      "job_responsibility_from_jd": "CI/CD experience",
      "suggested_bullet": "Implemented CI/CD pipelines using GitHub Actions.",
      "importance": "high"
    }
  ]
}
"""

@pytest.mark.asyncio
@patch("app.services.evaluate_resume.ChatOpenAI")
async def test_evaluate_resume_against_jd(mock_llm):
    # Mock LLM response
    mock_instance = AsyncMock()
    mock_instance.invoke.return_value.content = FAKE_LLM_RESPONSE
    mock_llm.return_value = mock_instance

    result = await evaluate_resume_against_jd(SAMPLE_RESUME_TEXT, SAMPLE_JD_TEXT)

    assert isinstance(result, ResumeEvaluationResult)
    assert result.ats_score == 85
    assert "CI/CD" in result.missing_keywords