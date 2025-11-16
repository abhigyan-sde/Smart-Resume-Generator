from typing import Optional
from app.services.evaluate_resume import build_resume_evaluation_prompt
from app.utils.validations import Validation
from app.utils.helper import Helper
from fastapi import HTTPException
from app.utils.parser import Parser
from app.models.resume_feedback import ResumeEvaluationResult


class OrchestratorService:
    """
    Service responsible for orchestrating the entire flow:
    - Validate resume file
    - Fetch job posting if URL provided
    - Extract text from resume
    - Send resume text and job description to evaluation service
    """

    def __init__(self):
        pass

    async def process_resume_and_job(
        file_bytes: bytes,
        filename: str,
        url: Optional[str] = None,
        job_text: Optional[str] = None,
    ) -> ResumeEvaluationResult:
        """
        Main orchestration entrypoint.

        Args:
            file_bytes (bytes): Uploaded resume file bytes.
            filename (str): Original filename of resume.
            url (Optional[str]): Job posting URL.
            job_text (Optional[str]): Raw job description text if pasted by user.

        Returns:
            Dict[str, Any]: Final state dictionary containing tailored resume.
        """
        print("begin Orchestrator")

        # ---- Step 1: Validate resume extension ----
        if not Validation.validateFileExtension(filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only PDF, DOC, DOCX allowed.",
            )

        # ---- Step 2: Handle job posting (url or job_text) ----
        extracted_job_text = job_text or (Helper.fetch_job_posting(url) if url else None)

        if not extracted_job_text:
            raise HTTPException(
                status_code=400,
                detail="Job description could not be retrieved. Please provide job text.",
            )

        resume_text = Parser.extract_resume_text_from_pdf(file_bytes)

        return await build_resume_evaluation_prompt(resume_text, extracted_job_text)
