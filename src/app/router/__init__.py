import os

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.model.api import ApiResumeParseRequest, ApiResumeParseResponse
from app.parser.pipeline1_gemini import Pipeline1Parser
from app.parser.pipeline2 import Pipeline2Parser
from app.parser.pipeline3 import Pipeline3Parser

router = APIRouter(prefix="/resume", tags=["resume"])

# Initialize all parsers
pipeline1_parser = Pipeline1Parser()
pipeline2_parser = Pipeline2Parser()
pipeline3_parser = Pipeline3Parser()


@router.post("/parse/pipeline1", response_model=ApiResumeParseResponse)
async def api_resume_parse_pipeline1(file: UploadFile = File(...)):
    """Parse resume using Pipeline 1 (Single LLM call)"""
    filename, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in [".docx", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .docx and .pdf files are accepted.",
        )

    result = await pipeline1_parser.parse_resume(file)
    print(f"Pipeline 1 - Cost: ${result.cost_estimate:.4f}, Tokens: {result.tokens_used}")
    
    await result.resume.insert()
    return ApiResumeParseResponse(resume=result.resume)


@router.post("/parse/pipeline2", response_model=ApiResumeParseResponse)
async def api_resume_parse_pipeline2(file: UploadFile = File(...)):
    """Parse resume using Pipeline 2 (Temperature-optimized multi-stage)"""
    filename, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in [".docx", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .docx and .pdf files are accepted.",
        )

    result = await pipeline2_parser.parse_resume(file)
    print(f"Pipeline 2 - Cost: ${result.cost_estimate:.4f}, Tokens: {result.tokens_used}")
    
    await result.resume.insert()
    return ApiResumeParseResponse(resume=result.resume)


@router.post("/parse/pipeline3", response_model=ApiResumeParseResponse)
async def api_resume_parse_pipeline3(file: UploadFile = File(...)):
    """Parse resume using Pipeline 3 (Hybrid Local + Cloud)"""
    filename, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in [".docx", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .docx and .pdf files are accepted.",
        )

    try:
        result = await pipeline3_parser.parse_resume(file)
        print(f"Pipeline 3 - Cost: ${result.cost:.4f}, Tokens: {result.tokens_used}")
        print(f"Pipeline 3 - Method: {result.method_used}, Time: {result.processing_time:.2f}s")
        print(f"Pipeline 3 - Local confidence: {result.local_confidence:.3f}, Cloud confidence: {result.cloud_confidence:.3f}")
        
        await result.resume.insert()
        return ApiResumeParseResponse(resume=result.resume)
    
    except Exception as e:
        print(f"Pipeline 3 error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline 3 parsing failed: {str(e)}"
        )


@router.post("/parse", response_model=ApiResumeParseResponse)
async def api_resume_parse_default(file: UploadFile = File(...)):
    """Default parse endpoint (uses Pipeline 3 - best accuracy/cost ratio)"""
    return await api_resume_parse_pipeline3(file)