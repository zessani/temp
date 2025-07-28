"""
Cloud processor using OpenAI for validation and enhancement.
Handles 20% of processing for accuracy boost and edge case handling.
"""

import json
import time
import openai
from dataclasses import dataclass
from typing import Dict, Any, Optional

from app.config.env_vars import EnvironmentVars

@dataclass
class CloudResult:
    success: bool
    data: Optional[Dict[str, Any]]
    confidence: float
    processing_time: float
    cost: float
    error: Optional[str] = None

class CloudProcessor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=EnvironmentVars.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        
    async def process(self, text: str) -> CloudResult:
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": f"Extract resume data:\n\n{text}"}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Calculate cost
            cost = self._calculate_cost(response.usage)
            confidence = self._calculate_confidence(data)
            
            return CloudResult(
                success=True,
                data=self._validate_structure(data),
                confidence=confidence,
                processing_time=time.time() - start_time,
                cost=cost
            )
            
        except Exception as e:
            return CloudResult(
                success=False,
                data=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                cost=0.0,
                error=str(e)
            )
    
    async def validate_and_enhance(self, local_data: Dict[str, Any], text: str) -> CloudResult:
        """Validate and enhance local processor results"""
        start_time = time.time()
        
        try:
            prompt = f"""Review and enhance this resume extraction:

LOCAL EXTRACTION:
{json.dumps(local_data, indent=2)}

ORIGINAL RESUME:
{text}

Tasks:
1. Verify all extracted information is accurate
2. Add any missing information 
3. Improve categorization and formatting
4. Fix any errors or inconsistencies

Return the corrected/enhanced JSON in the same format."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_enhancement_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            cost = self._calculate_cost(response.usage)
            confidence = self._calculate_confidence(data)
            
            return CloudResult(
                success=True,
                data=self._validate_structure(data),
                confidence=confidence,
                processing_time=time.time() - start_time,
                cost=cost
            )
            
        except Exception as e:
            return CloudResult(
                success=False,
                data=local_data, 
                confidence=0.7,
                processing_time=time.time() - start_time,
                cost=0.0,
                error=str(e)
            )
    
    def _get_system_prompt(self) -> str:
        return """You are an expert resume parser. Extract ALL information into JSON format.

CRITICAL RULES:
- Extract EVERY piece of information from the resume
- Use exact text from resume where possible
- Set null for missing fields, never omit them
- Categorize experience as "work", "project", or "volunteer"
- Group skills by logical categories (Programming, Tools, etc.)
- Parse dates correctly (year/month format)
- Preserve all bullet points in paragraphs arrays

Return valid JSON matching the exact schema provided."""

    def _get_enhancement_prompt(self) -> str:
        return """You are validating and enhancing resume extraction results.

TASKS:
1. Verify accuracy against original resume
2. Fix any extraction errors or missing data
3. Improve categorization and organization
4. Standardize formatting and dates
5. Enhance skill categorization

MAINTAIN:
- Original structure and schema
- All existing information
- Exact field names and types

Return enhanced JSON with improvements."""

    def _validate_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure data matches required schema"""
        defaults = {
            "personal_info": {
                "name": "Unknown",
                "email": None,
                "phone_number": None,
                "home_address": {"city": None, "state": None, "zip_code": None},
                "links": []
            },
            "education_items": [],
            "experience_items": [],
            "skills": [],
            "relevant_coursework": [],
            "paragraphs": []
        }
        
        for key, default in defaults.items():
            if key not in data:
                data[key] = default
        
        # Validate education items
        for item in data.get("education_items", []):
            if "location" not in item or not item["location"]:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            if "skills" not in item:
                item["skills"] = []
        
        # Validate experience items
        for item in data.get("experience_items", []):
            if "location" not in item or not item["location"]:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            if "paragraphs" not in item:
                item["paragraphs"] = []
            if "links" not in item:
                item["links"] = []
        
        return data
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence based on data completeness"""
        scores = []
        
        # Personal info score
        personal = data.get("personal_info", {})
        personal_score = sum([
            0.4 if personal.get("name") and personal["name"] != "Unknown" else 0,
            0.3 if personal.get("email") else 0,
            0.2 if personal.get("phone_number") else 0,
            0.1 if personal.get("links") else 0
        ])
        scores.append(personal_score)
        
        # Content completeness
        scores.append(min(1.0, len(data.get("education_items", [])) / 2))
        scores.append(min(1.0, len(data.get("experience_items", [])) / 3))
        scores.append(min(1.0, len(data.get("skills", [])) / 3))
        
        return sum(scores) / len(scores)
    
    def _calculate_cost(self, usage) -> float:
        """Calculate OpenAI API cost"""
        if not usage:
            return 0.0
        
        # GPT-4o-mini pricing
        input_cost = (usage.prompt_tokens / 1_000_000) * 0.15
        output_cost = (usage.completion_tokens / 1_000_000) * 0.60
        
        return input_cost + output_cost