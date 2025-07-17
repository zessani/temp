import time
from dataclasses import dataclass
from fastapi import UploadFile
from typing import Dict, Any

from app.parser.text_extract import extract_text_from_file
from app.model.schema.resume.together import Resume
from .extractors import Pipeline2Extractors
from .validator import Pipeline2Validator


@dataclass
class ParseResult:
    resume: Resume
    tokens_used: int
    processing_time: float
    cost_estimate: float


class Pipeline2Parser:
    def __init__(self):
        self.extractors = Pipeline2Extractors()
        self.validator = Pipeline2Validator()
    
    async def parse_resume(self, file: UploadFile) -> ParseResult:
        start_time = time.time()
        
        try:
            # Extract text from file
            resume_text = await extract_text_from_file(file)
            print(f"Extracted text length: {len(resume_text)} characters")
            
            # Stage 1: Comprehensive factual extraction (temp=0.0)
            print("Stage 1: Extracting comprehensive factual data...")
            factual_data = self.extractors.extract_facts(resume_text)
            
            if not factual_data:
                print("Warning: No factual data extracted")
                factual_data = self.extractors._get_empty_factual_structure()
            
            print(f"Factual data extracted: {len(factual_data)} sections")
            
            # Stage 2: Pattern recognition and categorization (temp=0.1)
            print("Stage 2: Recognizing patterns and categorizing...")
            pattern_data = self.extractors.recognize_patterns(resume_text, factual_data)
            
            if not pattern_data:
                print("Warning: No pattern data extracted")
                pattern_data = self.extractors._get_empty_pattern_structure()
            
            print(f"Pattern data extracted: {len(pattern_data)} categories")
            
            # Stage 3: Validation and schema mapping (temp=0.0)
            print("Stage 3: Validating and combining into final structure...")
            final_data = self.validator.validate_and_combine(factual_data, pattern_data)
            
            if not final_data:
                print("Warning: LLM validation failed, using fallback")
                final_data = self.validator._get_fallback_structure(factual_data, pattern_data)
            
            print(f"Final data structure created with {len(final_data)} sections")
            
            # Stage 4: Data cleaning and validation
            print("Stage 4: Cleaning and validating data...")
            cleaned_data = self.validator.clean_data(final_data)
            
            print(f"Data cleaned successfully")
            
            # Create resume object
            print("Creating Resume object...")
            resume = Resume.model_validate(cleaned_data)
            
            processing_time = time.time() - start_time
            tokens_used = self._estimate_tokens(resume_text, factual_data, pattern_data, final_data)
            cost = self._calculate_cost(tokens_used)
            
            print(f"Pipeline 2 completed in {processing_time:.2f}s")
            print(f"Estimated tokens used: {tokens_used}")
            print(f"Estimated cost: ${cost:.4f}")
            
            return ParseResult(resume, tokens_used, processing_time, cost)
            
        except Exception as e:
            print(f"Error in Pipeline 2: {e}")
            # Return a minimal fallback resume
            processing_time = time.time() - start_time
            fallback_resume = self._create_fallback_resume()
            return ParseResult(fallback_resume, 1000, processing_time, 0.01)
    
    def _estimate_tokens(self, text: str, factual_data: Dict[str, Any], pattern_data: Dict[str, Any], final_data: Dict[str, Any]) -> int:
        """Estimate total tokens for all API calls"""
        base_tokens = len(text.split()) * 1.3
        
        # Stage 1: Comprehensive factual extraction
        stage1_input = base_tokens + 1000  # Enhanced prompt
        stage1_output = len(str(factual_data).split()) * 1.3 if factual_data else 500
        
        # Stage 2: Pattern recognition with context
        stage2_input = base_tokens + len(str(factual_data).split()) * 1.3 + 1200
        stage2_output = len(str(pattern_data).split()) * 1.3 if pattern_data else 500
        
        # Stage 3: Detailed validation and mapping
        stage3_input = base_tokens + len(str(factual_data).split()) * 1.3 + len(str(pattern_data).split()) * 1.3 + 1400
        stage3_output = len(str(final_data).split()) * 1.3 if final_data else 500
        
        total_tokens = stage1_input + stage1_output + stage2_input + stage2_output + stage3_input + stage3_output
        
        return int(total_tokens)
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on Gemini Flash pricing"""
        # Gemini Flash pricing (approximate)
        input_cost = (tokens * 0.7) / 1_000_000 * 0.075  # 70% input tokens
        output_cost = (tokens * 0.3) / 1_000_000 * 0.30  # 30% output tokens
        return input_cost + output_cost
    
    def _create_fallback_resume(self) -> Resume:
        """Create a minimal fallback resume when parsing fails"""
        from app.model.schema.resume.info import ResumePersonalInfo
        from app.model.schema.resume.location import ResumeLocation
        
        return Resume(
            personal_info=ResumePersonalInfo(
                name="Unknown",
                home_address=ResumeLocation(
                    city=None,
                    state=None,
                    zip_code=None
                ),
                phone_number=None,
                email=None,
                links=[]
            ),
            education_items=[],
            skills=[],
            relevant_coursework=[],
            experience_items=[],
            paragraphs=[]
        )