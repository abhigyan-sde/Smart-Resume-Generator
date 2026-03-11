from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from app.models.resume_generation import ResumeGenerationPayLoad
from app.services.generate_resume import generate_resume_pdf
import json

router = APIRouter()

@router.post("/generate-resume")
async def generate_resume(payload: str = Form(...),
                          uploaded_file: UploadFile = File(...)):
    
    # Convert payload string → Pydantic model
    payload_dict = json.loads(payload)
    payload_obj = ResumeGenerationPayLoad(**payload_dict)

    pdf_bytes = await uploaded_file.read()

    pdf_stream = generate_resume_pdf(payload_obj, pdf_bytes)

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=optimized_resume.pdf"}
    )