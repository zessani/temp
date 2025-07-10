import io
from typing import Optional

from pypdf import PdfReader
from docx import Document
from fastapi import HTTPException, UploadFile


async def extract_text_from_file(file: UploadFile) -> str:
    try:
        content = await file.read()
        
        if file.filename and file.filename.lower().endswith('.pdf'):
            return _extract_from_pdf(content)
        elif file.filename and file.filename.lower().endswith('.docx'):
            return _extract_from_docx(content)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and DOCX files"
            )
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")


def _extract_from_pdf(content: bytes) -> str:
    """Extract text from PDF"""
    reader = PdfReader(io.BytesIO(content))
    text = ""
    
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text.strip()


def _extract_from_docx(content: bytes) -> str:
    """Extract text from DOCX"""
    doc = Document(io.BytesIO(content))
    text = ""
    
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"
    
    return text.strip()