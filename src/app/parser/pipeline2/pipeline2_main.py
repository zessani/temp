import time
from dataclasses import dataclass
from fastapi import UploadFile

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
        resume_text = await extract_text_from_file(file)
        
        # Stage 1: Comprehensive factual extraction (temp=0.0)
        print("Stage 1: Extracting comprehensive factual data...")
        factual_data = self.extractors.extract_facts(resume_text)
        
        # Stage 2: Pattern recognition and categorization (temp=0.1)
        print("Stage 2: Recognizing patterns and categorizing...")
        pattern_data = self.extractors.recognize_patterns(resume_text, factual_data)
        
        # Stage 3: Validation and schema mapping (temp=0.0)
        print("Stage 3: Validating and combining into final structure...")
        final_data = self.validator.validate_and_combine(factual_data, pattern_data)
        
        # Stage 4: Data cleaning and validation
        print("Stage 4: Cleaning and validating data...")
        cleaned_data = self.validator.clean_data(final_data)
        
        # Create resume object
        resume = Resume.model_validate(cleaned_data)
        
        processing_time = time.time() - start_time
        tokens_used = self._estimate_tokens(resume_text)
        cost = self._calculate_cost(tokens_used)
        
        print(f"Pipeline 2 completed in {processing_time:.2f}s")
        
        return ParseResult(resume, tokens_used, processing_time, cost)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate total tokens for 3 API calls with larger prompts"""
        base_tokens = len(text.split()) * 1.3
        
        # Enhanced prompts use more tokens
        stage1_tokens = base_tokens + 800   # Comprehensive factual extraction
        stage2_tokens = base_tokens + 1000  # Pattern recognition with context
        stage3_tokens = base_tokens + 1200  # Detailed validation and mapping
        
        return int(stage1_tokens + stage2_tokens + stage3_tokens)
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on Gemini Flash pricing"""
        input_cost = (tokens * 0.7) / 1_000_000 * 0.075  # 70% input
        output_cost = (tokens * 0.3) / 1_000_000 * 0.30  # 30% output
        return input_cost + output_cost