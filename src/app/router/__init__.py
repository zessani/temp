import os

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.model.api import ApiResumeParseRequest, ApiResumeParseResponse
from app.parser import parse_resume

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/parse", response_model=ApiResumeParseResponse)
async def api_resume_parse(file: UploadFile = File(...)):
    # Check the file extension
    filename, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in [".docx", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .docx and .pdf files are accepted.",
        )

    # Parse the resume file and get a "Resume" Beanie Document object.
    resume_doc = await parse_resume(file)

    # Insert it into a MongoDB collection named after the Beanie Document class name: "Resume."
    await resume_doc.insert()

    return ApiResumeParseResponse(resume=resume_doc)
