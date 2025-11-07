from typing import Optional, Dict, Any
from app.state_graph import run_pipeline
from app.utils.validations import Validation
from app.utils.helper import Helper
from fastapi import HTTPException
from app.utils.parser import Parser


class OrchestratorService:
    """
    Service responsible for orchestrating the entire flow:
    - Validate resume file
    - Fetch job posting if URL provided
    - Initialize and invoke LangGraph pipeline
    """

    @staticmethod
    def process_resume_and_job(
        file_bytes: bytes,
        filename: str,
        url: Optional[str] = None,
        job_text: Optional[str] = None,
    ) -> Dict[str, Any]:
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

        # ---- Step 3: Initialize state for LangGraph ----
        initial_state = {
            "resume_file_bytes": file_bytes,
            "resume_filename": filename,
            "job_text": extracted_job_text,
            "job_url": url,
        }

        final_state = run_pipeline(initial_state)

        # final_state["structured_resume_doc"]
        # final_state["job_description_doc"]
        # final_state["tailored_resume"]
        # final_state["pdf_bytes"]
        print("end orchestrator")
        return final_state
