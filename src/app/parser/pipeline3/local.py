"""
Local processor using Ollama + Llama 3.2 3B on M1 Mac.
Handles 80% of the processing for cost savings with good accuracy.
"""

import json
import time
import os
import re
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
        print(f"LocalProcessor connecting to: {self.host}")
        
    async def process(self, text: str) -> LocalResult:
        start_time = time.time()
        
        try:
            # Check if Ollama is available
            try:
                health_response = requests.get(f"{self.host}/api/tags", timeout=5)
                if health_response.status_code != 200:
                    raise Exception("Ollama not available")
            except:
                print("Ollama not available, returning fallback result")
                return LocalResult(
                    success=False,
                    data=self._get_empty_structure(),
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    error="Ollama not available"
                )
            
            prompt = self._create_optimized_prompt(text)
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_ctx": 4096,
                        "num_predict": 2048,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1
                    }
                },
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"Ollama error: {response.status_code}")
                return LocalResult(
                    success=False,
                    data=self._get_empty_structure(),
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    error=f"Ollama HTTP {response.status_code}"
                )
            
            result = response.json()
            generated = result.get('response', '')
            
            if not generated:
                print("Empty response from Ollama")
                return LocalResult(
                    success=False,
                    data=self._get_empty_structure(),
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    error="Empty response"
                )
            
            data = self._parse_response(generated)
            confidence = self._calculate_adaptive_confidence(data, text)
            
            return LocalResult(
                success=True,
                data=data,
                confidence=confidence,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            print(f"Local processor error: {e}")
            return LocalResult(
                success=False,
                data=self._get_empty_structure(),
                confidence=0.0,
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    def _create_optimized_prompt(self, text: str) -> str:
        return f"""Extract ALL information from this resume into JSON format with 95% accuracy. Be extremely thorough.

RESUME:
{text}

COMPREHENSIVE EXTRACTION STRATEGY:
1. SCAN ENTIRE DOCUMENT systematically for all sections
2. EXPERIENCE: Extract ALL positions from experience sections as type "work"
3. PROJECTS: Extract ALL projects from project sections as type "project"
4. SKILLS: Find ALL technical skills in dedicated skills sections AND within descriptions
5. COURSEWORK: Extract each course individually, never merge multiple courses
6. EDUCATION: Include complete degree with all majors, minors, specializations

CATEGORIZATION RULES:
- "work" for: jobs, internships, research, fellowships, teaching, consulting, medical roles
- "project" for: personal projects, hackathons, course projects, startups, apps, websites  
- "volunteer" for: unpaid community service, nonprofit work, religious organizations
- "technical" skills: programming languages, frameworks, tools, databases, platforms
- "transferable" skills: communication, leadership, teamwork, problem-solving

Extract into this EXACT JSON structure:
{{
  "personal_info": {{
    "name": "Full Name",
    "email": "email@domain.com or null", 
    "phone_number": "phone number or null",
    "home_address": {{"city": "City or null", "state": "State or null", "zip_code": null}},
    "links": ["linkedin", "github", "other"]
  }},
  "education_items": [
    {{
      "school_name": "Complete Institution Name",
      "degree": {{"study": "Complete Degree with Major, Minor, Concentrations", "type": "bachelors"}},
      "gpa": 3.5,
      "start_date": {{"year": 2023, "month": 8}},
      "end_date": {{"year": 2027, "month": 5}},
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "relevant_coursework": [
        {{"code": null, "name": "Individual Course Name 1"}},
        {{"code": null, "name": "Individual Course Name 2"}}
      ],
      "skills": []
    }}
  ],
  "experience_items": [
    {{
      "type": "work",
      "organization": "Complete Organization Name",
      "role": "Complete Job Title",
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "start_date": {{"year": 2024, "month": 1}},
      "end_date": null,
      "paragraphs": ["Complete bullet point 1", "Complete bullet point 2"],
      "links": []
    }},
    {{
      "type": "project",
      "organization": "Project Name or Context", 
      "role": "Role or Project Type",
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "start_date": {{"year": 2024, "month": 1}},
      "end_date": {{"year": 2024, "month": 5}},
      "paragraphs": ["Complete project description with technologies"],
      "links": []
    }}
  ],
  "skills": [
    {{"type": "technical", "category": "Programming Languages", "keywords": ["Language1", "Language2"]}},
    {{"type": "technical", "category": "Frameworks", "keywords": ["Framework1", "Framework2"]}},
    {{"type": "technical", "category": "Tools & Databases", "keywords": ["Tool1", "Database1"]}},
    {{"type": "transferable", "category": "Leadership", "keywords": ["Skill1", "Skill2"]}}
  ],
  "relevant_coursework": [],
  "paragraphs": []
}}

EXTRACTION REQUIREMENTS:
- Extract EVERY and ALL position from  work experience sections
- Extract EVERY project from project sections or project-based experience
- Find ALL technical skills from skills sections AND mentioned in descriptions
- Extract ALL courses individually from coursework sections
- Include complete degree information with all specializations
- Parse dates: "Sep 2024 - Present" = {{"year": 2024, "month": 9}}, end: null
- Preserve ALL bullet points exactly as written
- Use null for missing information

Return only valid JSON with complete extraction:"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        try:
            response = response.strip()
            
    
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                print("No JSON found in response")
                return self._get_empty_structure()
            
            json_str = response[start:end]
            
            json_str = re.sub(r'\s+', ' ', json_str)
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            json_str = re.sub(r'([{\[,])\s*,', r'\1', json_str)
            
            data = json.loads(json_str)
            return self._validate_and_enhance_structure(data)
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return self._extract_fallback_data(response)
        except Exception as e:
            print(f"Parse error: {e}")
            return self._get_empty_structure()
    
    def _extract_fallback_data(self, response: str) -> Dict[str, Any]:
        """Extract basic info if JSON parsing fails"""
        data = self._get_empty_structure()
        
        try:

            name_patterns = [
                r'"name":\s*"([^"]+)"',
                r'name:\s*"([^"]+)"',
                r'Name:\s*([^\n,]+)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    data["personal_info"]["name"] = match.group(1).strip()
                    break
            
            # Try to extract email
            email_match = re.search(r'"email":\s*"([^"]+@[^"]+)"', response, re.IGNORECASE)
            if email_match:
                data["personal_info"]["email"] = email_match.group(1)
            
        except Exception as e:
            print(f"Fallback extraction error: {e}")
        
        return data
    
    def _validate_and_enhance_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate structure optimized for 3B model output"""
 
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
            if key not in data or not data[key]:
                data[key] = default
        

        if not isinstance(data["personal_info"], dict):
            data["personal_info"] = defaults["personal_info"]
        else:
            personal = data["personal_info"]
            if "home_address" not in personal or not isinstance(personal["home_address"], dict):
                personal["home_address"] = {"city": None, "state": None, "zip_code": None}
            if "links" not in personal:
                personal["links"] = []
        

        for item in data.get("education_items", []):
            if "location" not in item:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            if "skills" not in item:
                item["skills"] = []
            if "relevant_coursework" not in item:
                item["relevant_coursework"] = []
         
            if "degree" not in item or not isinstance(item["degree"], dict):
                item["degree"] = {"study": None, "type": "other"}
            else:
                degree = item["degree"]
                if "type" not in degree or not degree["type"]:
                   
                    study = str(degree.get("study", "")).lower()
                    if "bachelor" in study or "bs" in study or "ba" in study:
                        degree["type"] = "bachelors"
                    elif "master" in study or "ms" in study or "ma" in study:
                        degree["type"] = "masters"
                    elif "phd" in study or "doctorate" in study:
                        degree["type"] = "phd"
                    elif "high school" in study:
                        degree["type"] = "high_school"
                    else:
                        degree["type"] = "other"
        
     
        for item in data.get("experience_items", []):
            if "location" not in item:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            if "paragraphs" not in item:
                item["paragraphs"] = []
            if "links" not in item:
                item["links"] = []
      
            if "type" not in item or item["type"] not in ["work", "project", "volunteer"]:
                item["type"] = "work" 
        
        # Validate skills
        for skill in data.get("skills", []):
            if "type" not in skill:
                skill["type"] = "technical"
            if "keywords" not in skill:
                skill["keywords"] = []
            if "category" not in skill:
                skill["category"] = "General"
        
        return data
    
    def _calculate_adaptive_confidence(self, data: Dict[str, Any], text: str) -> float:
        """Simplified confidence calculation for 3B model"""
        scores = []
        
        # Personal info score (30%)
        personal = data.get("personal_info", {})
        personal_score = 0
        if personal.get("name") and personal["name"] != "Unknown":
            personal_score += 0.7
        if personal.get("email"):
            personal_score += 0.3
        scores.append(personal_score)
        
        # Content extraction (70%)
        education_count = len(data.get("education_items", []))
        experience_count = len(data.get("experience_items", []))
        skills_count = sum(len(skill.get("keywords", [])) for skill in data.get("skills", []))
        
        # Simple scoring
        education_score = min(1.0, education_count / 2.0) if education_count > 0 else 0.5
        experience_score = min(1.0, experience_count / 2.0) if experience_count > 0 else 0.5
        skills_score = min(1.0, skills_count / 5.0) if skills_count > 0 else 0.3
        
        scores.extend([education_score, experience_score, skills_score])
        
        return sum(scores) / len(scores)
    
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