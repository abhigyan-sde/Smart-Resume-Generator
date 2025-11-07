from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from app.services.orchestrator import OrchestratorService
import io

router = APIRouter()

@router.post("/process")
async def process_resume_and_job(
    resume_file: UploadFile = File(..., description="Upload resume file (PDF or DOCX)"),
    job_url: str = Form(None, description="Job posting URL"),
    job_text: str = Form(None, description="Raw job posting text")
):
    print("Inside router for processing")
    """
    Accept a resume file and either a job posting URL or raw job description text.
    Orchestrates the pipeline to parse, tailor, and generate the tailored PDF resume.
    """
    if not job_url and not job_text:
        raise HTTPException(
            status_code=400,
            detail="Either 'job_url' or 'job description' must be provided."
        )

    try:
        # Read resume file bytes
        resume_bytes = await resume_file.read()

        # Call orchestrator
        result_state = OrchestratorService.process_resume_and_job(resume_bytes,resume_file.filename,
                                                                  job_url,job_text)

        # Extract tailored PDF
        pdf_bytes = result_state.get("pdf_bytes")
        if not pdf_bytes:
            raise HTTPException(
                status_code=500,
                detail="Pipeline completed but PDF was not generated."
            )

        # Stream PDF back as response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=tailored_resume.pdf"}
        )

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Parsing error: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")