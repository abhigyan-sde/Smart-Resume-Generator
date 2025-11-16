from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends, File
from fastapi.responses import StreamingResponse
from app.services.orchestrator import OrchestratorService
from app.di.dependencies import getOrchestratorService
import json

router = APIRouter()

@router.post("/process")
async def process_resume_and_job(
    resume_file: UploadFile = File(..., description="Upload resume file (PDF or DOCX)"),
    job_url: str = Form(None, description="Job posting URL"),
    job_text: str = Form(None, description="Raw job posting text"),
    orchestrator: OrchestratorService = Depends(getOrchestratorService),
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
        result: dict = orchestrator.process_resume_and_job(resume_bytes,resume_file.filename,
                                                                  job_url,job_text)

        # Extract tailored PDF
        async def json_streamer():
            json_str = json.dumps(result.model_dump())  # Use Pydantic's serialization
            yield json_str

        return StreamingResponse(
            json_streamer(),
            media_type="application/json"
        )


    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Parsing error: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")