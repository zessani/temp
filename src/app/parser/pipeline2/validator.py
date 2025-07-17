import google.generativeai as genai
import json
from typing import Dict

from app.config.env_vars import EnvironmentVars


class Pipeline2Validator:
    def __init__(self):
        genai.configure(api_key=EnvironmentVars.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def validate_and_combine(self, factual: Dict, patterns: Dict) -> Dict:
        """Validate and combine into final resume structure (temp=0.0)"""
        prompt = f"""Combine the factual data and patterns into the EXACT resume schema. Preserve ALL information.

CRITICAL RULES:
1. NEVER lose any information from the factual data
2. Use patterns for categorization but keep all factual details
3. Ensure ALL bullet points are preserved in paragraphs arrays
4. Ensure ALL coursework is preserved
5. Ensure ALL skills are preserved and properly categorized
6. Ensure ALL links are preserved with proper platforms

EXACT SCHEMA TO MATCH:
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
      "school_name": "Full University Name",
      "degree": {{"study": "Complete Degree Description", "type": "bachelors"}},
      "gpa": 3.5,
      "start_date": {{"year": 2023, "month": 8}},
      "end_date": {{"year": 2027, "month": 5}},
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "relevant_coursework": [
        {{"code": null, "name": "Course Name 1"}},
        {{"code": null, "name": "Course Name 2"}}
      ],
      "skills": []
    }}
  ],
  "experience_items": [
    {{
      "type": "work",
      "organization": "Full Organization Name",
      "role": "Complete Job Title",
      "location": {{"city": "City", "state": "State", "zip_code": null}},
      "start_date": {{"year": 2024, "month": 9}},
      "end_date": null,
      "paragraphs": [
        "Complete bullet point 1 from factual data",
        "Complete bullet point 2 from factual data",
        "Complete bullet point 3 from factual data"
      ],
      "links": []
    }}
  ],
  "skills": [
    {{"type": "technical", "category": "Programming Languages", "keywords": ["Python", "JavaScript"]}},
    {{"type": "technical", "category": "Frameworks", "keywords": ["React", "Next.js"]}},
    {{"type": "transferable", "category": "Leadership", "keywords": ["Communication", "Teamwork"]}}
  ],
  "relevant_coursework": [],
  "paragraphs": []
}}

CRITICAL: 
- ALL experience bullet points must be in paragraphs arrays
- ALL coursework must be in relevant_coursework arrays
- ALL skills must be properly categorized
- ALL links must have proper platform identification

Factual data: {json.dumps(factual)}
Pattern data: {json.dumps(patterns)}

Return the complete resume following the exact schema above:"""
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=8192,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    
    def clean_data(self, data: Dict) -> Dict:
        """Clean and ensure data structure completeness"""
        # Ensure all required fields exist
        defaults = {
            "education_items": [],
            "experience_items": [],
            "skills": [],
            "relevant_coursework": [],
            "paragraphs": []
        }
        
        for key, default in defaults.items():
            if key not in data:
                data[key] = default
        
        # Validate personal info
        if "personal_info" in data:
            personal = data["personal_info"]
            if personal.get("home_address") is None:
                personal["home_address"] = {"city": None, "state": None, "zip_code": None}
            
            # Ensure links are properly formatted
            if "links" in personal and personal["links"]:
                cleaned_links = []
                for link in personal["links"]:
                    if isinstance(link, str):
                        cleaned_links.append(link)
                    elif isinstance(link, dict):
                        if "platform" in link:
                            cleaned_links.append(link["platform"])
                        elif "url" in link:
                            # Determine platform from URL
                            url = link["url"].lower()
                            if "linkedin" in url:
                                cleaned_links.append("linkedin")
                            elif "github" in url:
                                cleaned_links.append("github")
                            else:
                                cleaned_links.append("other")
                personal["links"] = cleaned_links
        
        # Validate education items
        for item in data.get("education_items", []):
            if item.get("location") is None:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            
            # Ensure coursework has proper structure
            if "relevant_coursework" in item:
                for course in item["relevant_coursework"]:
                    if not isinstance(course, dict):
                        course = {"code": None, "name": str(course)}
                    if "code" not in course:
                        course["code"] = None
                    if "name" not in course:
                        course["name"] = str(course)
        
        # Validate experience items
        for item in data.get("experience_items", []):
            if item.get("location") is None:
                item["location"] = {"city": None, "state": None, "zip_code": None}
            
            # Ensure paragraphs exist and are strings
            if "paragraphs" not in item:
                item["paragraphs"] = []
            elif item["paragraphs"]:
                item["paragraphs"] = [str(p) for p in item["paragraphs"] if p]
        
        # Validate skills
        for skill in data.get("skills", []):
            if "keywords" not in skill:
                skill["keywords"] = []
            elif skill["keywords"]:
                skill["keywords"] = [str(k) for k in skill["keywords"] if k]
        
        return data