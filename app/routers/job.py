from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.job_parser import JobParser
from app.models.job_models import JobDescriptionDocument

router = APIRouter()

class JobParseRequest(BaseModel):
    url: str

@router.post("/parse", response_model=JobDescriptionDocument)
async def parse_job(request: JobParseRequest):
    """
    Accept a job posting URL, scrape the content, and parse it into structured fields.
    """
    try:
        job_doc = JobParser.parse_job_posting(request.url)
        return job_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
