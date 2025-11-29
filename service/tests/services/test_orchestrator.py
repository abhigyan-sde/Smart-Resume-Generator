import pytest
from unittest.mock import AsyncMock, patch
from app.services.orchestrator import OrchestratorService


@pytest.mark.asyncio
async def test_process_resume_and_job_success():
    service = OrchestratorService()
    print("Before call:", service.process_resume_and_job)

    with (
        patch("app.services.orchestrator.Validation.validateFileExtension", return_value=True),
        patch("app.services.orchestrator.Helper.fetch_job_posting", return_value="JD TEXT"),
        patch("app.services.orchestrator.Parser.extract_resume_text_from_pdf", return_value="RESUME TEXT"),
        patch("app.services.orchestrator.evaluate_resume_against_jd", new=AsyncMock(return_value={"ats_score": 90}))
    ):
        result = await service.process_resume_and_job(
            file_bytes=b"dummy",
            filename="resume.pdf",
            url=None,
            job_text="JD TEXT"
        )

        assert result["ats_score"] == 90
