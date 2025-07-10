import google.generativeai as genai
import json
import time
from dataclasses import dataclass
from fastapi import UploadFile

from app.parser.text_extract import extract_text_from_file
from app.model.schema.resume.together import Resume
from app.config.env_vars import EnvironmentVars

@dataclass
class ParseResult:
    resume: Resume
    tokens_used: int
    processing_time: float
    cost_estimate: float

class Pipeline1Parser:
    def __init__(self):
        genai.configure(api_key=EnvironmentVars.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def parse_resume(self, file: UploadFile) -> ParseResult:
        start_time = time.time()
        resume_text = await extract_text_from_file(file)
        
        prompt = f"""Extract ALL information from this resume into JSON. Follow these rules exactly:

CATEGORIZATION RULES:
- experience_items.type: 
  * "work" for paid jobs, internships, research positions, leadership roles, medical shadowing
  * "project" for personal projects, hackathons, course projects, startups
  * "volunteer" for unpaid community service, religious organizations
- Research positions = "work" (even if undergraduate)
- Medical shadowing = "work" with role "Medical Observer" or "Medical Student"
- Leadership roles = "work" 
- Put skills ONLY in root "skills" array, NOT in education_items
- Extract ALL dates - parse "2023-present", "2023-2025", "May 2025-present" carefully
- Extract ALL role titles - never leave null if any title/position exists
- Group related activities under same organization when possible

JSON STRUCTURE:
{{
  "personal_info": {{
    "name": "Full Name",
    "home_address": {{"city": "City", "state": "State", "zip_code": null}},
    "phone_number": "phone if available",
    "email": "email@domain.com", 
    "links": ["linkedin", "github", "other"]
  }},
  "education_items": [
    {{
      "school_name": "University Name",
      "degree": {{"study": "Complete degree with any minors", "type": "bachelors"}},
      "gpa": 3.5,
      "start_date": {{"year": 2023, "month": 8}},
      "end_date": {{"year": 2026, "month": 5}},
      "location": {{"city": "Tucson", "state": "AZ", "zip_code": null}},
      "relevant_coursework": [
        {{"code": null, "name": "Course Name"}}
      ],
      "skills": []
    }}
  ],
  "experience_items": [
    {{
      "type": "work",
      "organization": "Company/Lab Name", 
      "role": "Exact Job Title from Resume or Medical Observer",
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "start_date": {{"year": 2024, "month": 9}},
      "end_date": null,
      "paragraphs": ["Bullet 1", "Bullet 2"],
      "links": []
    }}
  ],
  "skills": [
    {{"type": "technical", "category": "Programming", "keywords": ["Python", "Java"]}},
    {{"type": "technical", "category": "Tools", "keywords": ["Git", "Docker"]}},
    {{"type": "transferable", "category": "Leadership", "keywords": ["Communication", "Teamwork"]}}
  ],
  "relevant_coursework": [],
  "paragraphs": []
}}

CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:
1. DATES: "2023-present" = start: {{year: 2023, month: null}}, end: null
2. DATES: "May 2025-present" = start: {{year: 2025, month: 5}}, end: null  
3. DATES: "2023-2025" = start: {{year: 2023, month: null}}, end: {{year: 2025, month: null}}
4. ROLES: If no exact title, infer appropriate role (e.g., "Medical Observer", "Research Assistant", "Project Lead")
5. ORGANIZATION: Don't leave null - use project name, department, or company name
6. LOCATION: Extract from context if available (university location, company headquarters, etc.)
7. GROUP RELATED: Multiple roles at same organization should be separate experience_items
8. RESEARCH PROJECTS: Keep as part of the lab/organization, don't separate into standalone projects

Resume:
{resume_text}"""
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=8192,
                response_mime_type="application/json"
            )
        )
        
        processing_time = time.time() - start_time
        tokens_used = self._estimate_tokens(prompt, response.text)
        cost = self._calculate_cost(prompt, response.text)
        
        parsed_data = json.loads(response.text)
        self._clean_data(parsed_data)
        resume = Resume.model_validate(parsed_data)
        
        return ParseResult(resume, tokens_used, processing_time, cost)
    
    def _estimate_tokens(self, input_text: str, output_text: str) -> int:
        input_tokens = len(input_text.split()) * 1.3
        output_tokens = len(output_text.split()) * 1.3
        return int(input_tokens + output_tokens)
    
    def _calculate_cost(self, input_text: str, output_text: str) -> float:
        input_tokens = len(input_text.split()) * 1.3
        output_tokens = len(output_text.split()) * 1.3
        
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.30
        
        return input_cost + output_cost
    
    def _clean_data(self, data):
        # Fix links
        if "personal_info" in data and "links" in data["personal_info"]:
            cleaned_links = []
            for link in data["personal_info"]["links"]:
                if "linkedin" in str(link).lower():
                    cleaned_links.append("linkedin")
                elif "github" in str(link).lower():
                    cleaned_links.append("github")
                else:
                    cleaned_links.append("other")
            data["personal_info"]["links"] = cleaned_links
        
    
        for item in data.get("education_items", []):
            for course in item.get("relevant_coursework", []):
                if not course.get("code"):
                    course["code"] = None
            
            if item.get("location") is None:
                item["location"] = {"city": None, "state": None, "zip_code": None}
        
        for item in data.get("experience_items", []):
            if item.get("location") is None:
                item["location"] = {"city": None, "state": None, "zip_code": None}
                    

        defaults = {"education_items": [], "experience_items": [], "skills": [], "relevant_coursework": [], "paragraphs": []}
        for key, default in defaults.items():
            if key not in data:
                data[key] = default