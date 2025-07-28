"""
Local processor using Ollama + Llama 3.2 on M1 Mac.
Handles 80% of the processing for cost savings with good accuracy.
"""

import json
import time
import os
import requests
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class LocalResult:
    success: bool
    data: Optional[Dict[str, Any]]
    confidence: float
    processing_time: float
    error: Optional[str] = None

class LocalProcessor:
    def __init__(self, host: str = None):
        # Use environment variable or default
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = "llama3.2:3b-instruct-q4_0"
        print(f"LocalProcessor connecting to: {self.host}")  # Debug log
        
    async def process(self, text: str) -> LocalResult:
        start_time = time.time()
        
        try:
            prompt = self._create_prompt(text)
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_ctx": 4096
                    }
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code}")
            
            result = response.json()
            generated = result.get('response', '')
            
            data = self._parse_response(generated)
            confidence = self._calculate_confidence(data, text)
            
            return LocalResult(
                success=True,
                data=data,
                confidence=confidence,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return LocalResult(
                success=False,
                data=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    def _create_prompt(self, text: str) -> str:
        return f"""Extract resume information into JSON format.

RESUME:
{text}

Extract into this exact JSON structure:
{{
  "personal_info": {{
    "name": "Full Name",
    "email": "email@domain.com",
    "phone_number": "phone or null",
    "home_address": {{"city": "City", "state": "State", "zip_code": null}},
    "links": ["linkedin", "github", "other"]
  }},
  "education_items": [
    {{
      "school_name": "University Name",
      "degree": {{"study": "Degree Major", "type": "bachelors"}},
      "gpa": 3.5,
      "start_date": {{"year": 2023, "month": 8}},
      "end_date": {{"year": 2027, "month": 5}},
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "relevant_coursework": [{{"code": null, "name": "Course Name"}}],
      "skills": []
    }}
  ],
  "experience_items": [
    {{
      "type": "work",
      "organization": "Company Name",
      "role": "Job Title",
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "start_date": {{"year": 2024, "month": 1}},
      "end_date": null,
      "paragraphs": ["Bullet point 1", "Bullet point 2"],
      "links": []
    }}
  ],
  "skills": [
    {{"type": "technical", "category": "Programming", "keywords": ["Python", "Java"]}}
  ],
  "relevant_coursework": [],
  "paragraphs": []
}}

Extract ALL information. Use null for missing data. Return only valid JSON:"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                return self._get_empty_structure()
            
            json_str = response[start:end]
            data = json.loads(json_str)
            
            return self._validate_structure(data)
            
        except:
            return self._get_empty_structure()
    
    def _validate_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure required keys exist
        defaults = {
            "personal_info": {"name": "Unknown", "email": None, "phone_number": None, 
                            "home_address": {"city": None, "state": None, "zip_code": None}, "links": []},
            "education_items": [],
            "experience_items": [],
            "skills": [],
            "relevant_coursework": [],
            "paragraphs": []
        }
        
        for key, default in defaults.items():
            if key not in data:
                data[key] = default
        
        return data
    
    def _calculate_confidence(self, data: Dict[str, Any], text: str) -> float:
        scores = []
        
        # Personal info completeness
        personal = data.get("personal_info", {})
        personal_score = 0
        if personal.get("name") and personal["name"] != "Unknown":
            personal_score += 0.4
        if personal.get("email"):
            personal_score += 0.3
        if personal.get("phone_number"):
            personal_score += 0.3
        scores.append(personal_score)
        
        # Education presence
        education_score = min(1.0, len(data.get("education_items", [])) / 2)
        scores.append(education_score)
        
        # Experience presence  
        experience_score = min(1.0, len(data.get("experience_items", [])) / 3)
        scores.append(experience_score)
        
        # Skills presence
        skills_score = min(1.0, len(data.get("skills", [])) / 3)
        scores.append(skills_score)
        
        return sum(scores) / len(scores)
    
    def _get_empty_structure(self) -> Dict[str, Any]:
        return {
            "personal_info": {"name": "Unknown", "email": None, "phone_number": None,
                            "home_address": {"city": None, "state": None, "zip_code": None}, "links": []},
            "education_items": [],
            "experience_items": [],
            "skills": [],
            "relevant_coursework": [],
            "paragraphs": []
        }