from app.models.resume_feedback import ResumeEvaluationResult

def test_process_resume_and_job_router(client, mock_orchestrator):

    mock_Result = ResumeEvaluationResult(
        ats_score=92,
        summary="Strong fit",
        missing_keywords=["CI/CD"],
        skills_match={"matched_skills": ["APIs"], "unmatched_skills": ["CI/CD"]},
        section_feedback=[],
        line_by_line_suggestions=[],
        recommended_new_bullets=[]
    )

    mock_orchestrator.process_resume_and_job.return_value = mock_Result

    files = {
        "resume_file": ("resume.pdf", b"fake-resume-content", "application/pdf")
    }
    data = {
        "job_text": "We are looking for a software engineer with API and CI/CD experience."
    }

    # Call the endpoint
    response = client.post("/resume/process", files=files, data=data)

    # --- Assertions ---
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    # Check JSON content returned by the mock orchestrator
    json_data = response.json()
    assert "ats_score" in json_data
    assert json_data["ats_score"] == 92  # Base64-encoded b"PDF" since FastAPI JSON serializes bytes

    # Verify the orchestrator method was called
    mock_orchestrator.process_resume_and_job.assert_awaited_once()
