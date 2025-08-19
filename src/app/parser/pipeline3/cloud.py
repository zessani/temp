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
        if not EnvironmentVars.OPENAI_API_KEY:
            print("Warning: No OpenAI API key found")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=EnvironmentVars.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        
    async def process(self, text: str) -> CloudResult:
        start_time = time.time()
        
        if not self.client:
            return CloudResult(
                success=False,
                data=self._get_empty_structure(),
                confidence=0.0,
                processing_time=time.time() - start_time,
                cost=0.0,
                error="No OpenAI API key"
            )
        
        try:
            # Truncate text if too long
            if len(text) > 8000:
                text = text[:8000] + "..."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_adaptive_system_prompt()},
                    {"role": "user", "content": f"Extract ALL resume information with perfect accuracy:\n\n{text}"}
                ],
                temperature=0.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("Empty response from OpenAI")
            
            data = json.loads(content)
            
            cost = self._calculate_cost(response.usage)
            confidence = self._calculate_adaptive_confidence(data, text)
            
            return CloudResult(
                success=True,
                data=self._validate_structure(data),
                confidence=confidence,
                processing_time=time.time() - start_time,
                cost=cost
            )
            
        except Exception as e:
            print(f"Cloud processor error: {e}")
            return CloudResult(
                success=False,
                data=self._get_empty_structure(),
                confidence=0.0,
                processing_time=time.time() - start_time,
                cost=0.0,
                error=str(e)
            )
    
    def _get_adaptive_system_prompt(self) -> str:
        return """You are an expert resume parser. Extract ALL information into the EXACT JSON format specified.

EXTRACTION RULES:
1. EXPERIENCE: Extract ALL positions from experience sections as type "work"
2. PROJECTS: Extract ALL projects from project sections as type "project"
3. SKILLS: Find ALL technical skills in skills sections AND embedded in descriptions
4. EDUCATION: Include complete degree with majors, minors, specializations
5. COURSEWORK: Extract each course individually

CATEGORIZATION:
- "work": jobs, internships, research, fellowships, teaching, consulting, medical roles
- "project": personal projects, hackathons, course projects, startups, apps
- "volunteer": unpaid community service, nonprofit work, religious organizations

Return ONLY valid JSON in this EXACT structure:
{
  "personal_info": {
    "name": "Full Name",
    "email": "email@domain.com",
    "phone_number": "phone or null",
    "home_address": {"city": "City", "state": "State", "zip_code": null},
    "links": ["linkedin", "github", "other"]
  },
  "education_items": [
    {
      "school_name": "University Name",
      "degree": {"study": "Complete Degree with Major, Minor", "type": "bachelors"},
      "gpa": 3.5,
      "start_date": {"year": 2023, "month": 8},
      "end_date": {"year": 2027, "month": 5},
      "location": {"city": "City", "state": "State", "zip_code": null},
      "relevant_coursework": [
        {"code": null, "name": "Course Name 1"},
        {"code": null, "name": "Course Name 2"}
      ],
      "skills": []
    }
  ],
  "experience_items": [
    {
      "type": "work",
      "organization": "Company Name",
      "role": "Job Title",
      "location": {"city": "City", "state": "State", "zip_code": null},
      "start_date": {"year": 2024, "month": 1},
      "end_date": null,
      "paragraphs": ["Bullet point 1", "Bullet point 2"],
      "links": []
    }
  ],
  "skills": [
    {"type": "technical", "category": "Programming Languages", "keywords": ["Python", "Java"]},
    {"type": "transferable", "category": "Leadership", "keywords": ["Communication"]}
  ],
  "relevant_coursework": [],
  "paragraphs": []
}

CRITICAL REQUIREMENTS:
- Extract EVERY position from experience sections
- Extract EVERY project from project sections
- Find ALL technical skills mentioned anywhere
- Use null for missing data, never omit required fields
- Parse dates as {"year": YYYY, "month": MM} format
- Include ALL bullet points in paragraphs arrays"""
    def _validate_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate structure adaptively"""
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

        def fix_coursework_format(coursework_list):
            if not coursework_list:
                return []
            
            fixed_coursework = []
            for item in coursework_list:
                if isinstance(item, str):
                    fixed_coursework.append({"code": None, "name": item})
                elif isinstance(item, dict):
                    if "name" not in item:
                        item["name"] = str(item.get("code", "Unknown Course"))
                    if "code" not in item:
                        item["code"] = None
                    fixed_coursework.append(item)
            return fixed_coursework
        
        data["relevant_coursework"] = fix_coursework_format(data.get("relevant_coursework", []))
        
        # Validate education items
        for item in data.get("education_items", []):
            if "location" not in item or not item["location"]:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            if "skills" not in item:
                item["skills"] = []
            if "relevant_coursework" not in item:
                item["relevant_coursework"] = []
            else:
                item["relevant_coursework"] = fix_coursework_format(item["relevant_coursework"])
            
            # Fix degree structure
            if "degree" not in item or not isinstance(item["degree"], dict):
                item["degree"] = {"study": None, "type": "other"}
            else:
                degree = item["degree"]
                if "type" not in degree or not degree["type"]:
        
                    study = degree.get("study", "").lower()
                    if any(word in study for word in ["bachelor", "bs", "ba", "b.s", "b.a"]):
                        degree["type"] = "bachelors"
                    elif any(word in study for word in ["master", "ms", "ma", "mba", "m.s", "m.a"]):
                        degree["type"] = "masters"
                    elif any(word in study for word in ["phd", "ph.d", "doctorate", "doctoral"]):
                        degree["type"] = "phd"
                    elif any(word in study for word in ["high school", "diploma", "ged"]):
                        degree["type"] = "high_school"
                    else:
                        degree["type"] = "other"
                if "study" not in degree:
                    degree["study"] = None
        
        # Validate experience items
        for item in data.get("experience_items", []):
            if "location" not in item or not item["location"]:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            if "paragraphs" not in item:
                item["paragraphs"] = []
            if "links" not in item:
                item["links"] = []
        
        return data
    
    def _calculate_adaptive_confidence(self, data: Dict[str, Any], text: str) -> float:
        """Calculate confidence adaptively based on resume content"""
        scores = []
        
        # Personal info score (25%)
        personal = data.get("personal_info", {})
        personal_score = 0
        if personal.get("name") and personal["name"] != "Unknown":
            personal_score += 0.5
        if personal.get("email"):
            personal_score += 0.3
        if personal.get("links"):
            personal_score += 0.2
        scores.append(personal_score)
        
        text_lower = text.lower()
        
      
        education_items = len(data.get("education_items", []))
        has_education_indicators = any(word in text_lower for word in 
            ["university", "college", "degree", "bachelor", "master", "phd", "education", "school"])
        
        if has_education_indicators:
            education_score = min(1.0, education_items / 2.0) if education_items > 0 else 0.3
        else:
            education_score = 0.9 
        scores.append(education_score)
        
      
        experience_items = len(data.get("experience_items", []))
        has_experience_indicators = any(word in text_lower for word in 
            ["experience", "work", "position", "intern", "research", "project", "leadership", "clinical"])
        
        if has_experience_indicators:
            experience_score = min(1.0, experience_items / 4.0) if experience_items > 0 else 0.2
        else:
            experience_score = 0.9  
        scores.append(experience_score)
        
       
        total_skills = sum(len(skill.get("keywords", [])) for skill in data.get("skills", []))
        has_skills_indicators = any(word in text_lower for word in 
            ["skill", "programming", "language", "tool", "technology", "software", "technical"])
        
        if has_skills_indicators:
            skills_score = min(1.0, total_skills / 10.0) if total_skills > 0 else 0.2
        else:
            skills_score = 0.9  
        scores.append(skills_score)
        
        return sum(scores) / len(scores)
    
    def _calculate_cost(self, usage) -> float:
        """Calculate OpenAI API cost"""
        if not usage:
            return 0.0
        
        input_cost = (usage.prompt_tokens / 1_000_000) * 0.15
        output_cost = (usage.completion_tokens / 1_000_000) * 0.60
        
        return input_cost + output_cost
    
    def _get_empty_structure(self) -> Dict[str, Any]:
        return {
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