import os

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.model.api import ApiResumeParseRequest, ApiResumeParseResponse
from app.parser.pipeline1_gemini import Pipeline1Parser
from app.parser.pipeline2 import Pipeline2Parser

router = APIRouter(prefix="/resume", tags=["resume"])

# Initialize both parsers
pipeline1_parser = Pipeline1Parser()
pipeline2_parser = Pipeline2Parser()


@router.post("/parse/pipeline1", response_model=ApiResumeParseResponse)
async def api_resume_parse_pipeline1(file: UploadFile = File(...)):
    """Parse resume using Pipeline 1 (Single LLM call)"""
    # Check the file extension
    filename, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in [".docx", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .docx and .pdf files are accepted.",
        )

    # Parse with Pipeline 1
    result = await pipeline1_parser.parse_resume(file)
    print(f"Pipeline 1 - Cost: ${result.cost_estimate:.4f}, Tokens: {result.tokens_used}")
    
    # Insert into database
    await result.resume.insert()

    return ApiResumeParseResponse(resume=result.resume)


@router.post("/parse/pipeline2", response_model=ApiResumeParseResponse)
async def api_resume_parse_pipeline2(file: UploadFile = File(...)):
    """Parse resume using Pipeline 2 (Temperature-optimized multi-stage)"""
    # Check the file extension
    filename, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in [".docx", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .docx and .pdf files are accepted.",
        )

    try:
        # Parse with Pipeline 2
        result = await pipeline2_parser.parse_resume(file)
        print(f"Pipeline 2 - Cost: ${result.cost_estimate:.4f}, Tokens: {result.tokens_used}")
        
        # Insert into database
        await result.resume.insert()

        return ApiResumeParseResponse(resume=result.resume)
    
    except Exception as e:
        print(f"Pipeline 2 error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline 2 parsing failed: {str(e)}"
        )


@router.post("/parse", response_model=ApiResumeParseResponse)
async def api_resume_parse_default(file: UploadFile = File(...)):
    """Default parse endpoint (uses Pipeline 1)"""
    return await api_resume_parse_pipeline1(file)