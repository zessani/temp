import google.generativeai as genai
import json
from typing import Dict, Any, List

from app.config.env_vars import EnvironmentVars


class Pipeline2Validator:
    def __init__(self):
        genai.configure(api_key=EnvironmentVars.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def validate_and_combine(self, factual: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and combine into final resume structure (temp=0.0)"""
        prompt = f"""Combine the factual data and pattern categorization into the EXACT resume schema. You must preserve ALL information from the factual data.

CRITICAL RULES:
1. NEVER lose any information from the factual data
2. Use pattern categorization for structure but keep all factual details
3. Ensure ALL bullet points are preserved in paragraphs arrays
4. Ensure ALL coursework is preserved
5. Ensure ALL skills are preserved and properly categorized
6. Ensure ALL links are preserved with proper platform identification
7. Fill in missing information with null values, never omit fields

EXACT SCHEMA TO MATCH:
{{
  "personal_info": {{
    "name": "Full Name From Factual Data",
    "email": "email@domain.com or null",
    "phone_number": "phone number or null",
    "home_address": {{
      "city": "City Name or null",
      "state": "State Name or null",
      "zip_code": "Zip Code or null"
    }},
    "links": ["linkedin", "github", "other"]
  }},
  "education_items": [
    {{
      "school_name": "Full University Name",
      "degree": {{
        "study": "Complete Degree Description with Major/Minor",
        "type": "bachelors"
      }},
      "gpa": 3.5,
      "start_date": {{"year": 2023, "month": 8}},
      "end_date": {{"year": 2027, "month": 5}},
      "location": {{
        "city": "City Name or null",
        "state": "State Name or null",
        "zip_code": null
      }},
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
      "location": {{
        "city": "City Name or null",
        "state": "State Name or null",
        "zip_code": null
      }},
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
    {{
      "type": "technical",
      "category": "Programming Languages",
      "keywords": ["Python", "JavaScript"]
    }},
    {{
      "type": "technical",
      "category": "Frameworks",
      "keywords": ["React", "Next.js"]
    }},
    {{
      "type": "transferable",
      "category": "Leadership",
      "keywords": ["Communication", "Teamwork"]
    }}
  ],
  "relevant_coursework": [],
  "paragraphs": []
}}

MAPPING INSTRUCTIONS:
1. Personal Info:
   - Use factual.personal data
   - Convert links to platform names only (linkedin, github, other)
   - Map address fields correctly

2. Education Items:
   - Use factual.education and patterns.education_categorization
   - Map degree types correctly (bachelors, masters, phd, high_school)
   - Convert coursework to proper format with code and name
   - Parse dates according to pattern categorization

3. Experience Items:
   - Use factual.experiences and patterns.experience_categorization
   - Map types correctly (work, project, volunteer)
   - ALL bullets must go into paragraphs array
   - Parse dates according to pattern categorization

4. Skills:
   - Use factual.skills and patterns.skills_categorization
   - Map types correctly (technical, transferable)
   - Group by category (Programming Languages, Frameworks, etc.)
   - Convert items to keywords array

5. Default Values:
   - Use null for missing optional fields
   - Use empty arrays for missing lists
   - Ensure all required fields are present

Factual Data:
{json.dumps(factual, indent=2)}

Pattern Data:
{json.dumps(patterns, indent=2)}

Return the complete resume following the exact schema above. Ensure no information is lost:"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in validate_and_combine: {e}")
            return self._get_fallback_structure(factual, patterns)
    
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and ensure data structure completeness"""
        # Ensure all required top-level fields exist
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
        
        # Clean personal info
        self._clean_personal_info(data["personal_info"])
        
        # Clean education items
        for item in data["education_items"]:
            self._clean_education_item(item)
        
        # Clean experience items
        for item in data["experience_items"]:
            self._clean_experience_item(item)
        
        # Clean skills
        for skill in data["skills"]:
            self._clean_skill_item(skill)
        
        # Clean relevant coursework
        data["relevant_coursework"] = self._clean_coursework(data["relevant_coursework"])
        
        # Ensure paragraphs is a list of strings
        if data["paragraphs"]:
            data["paragraphs"] = [str(p) for p in data["paragraphs"] if p and str(p).strip()]
        
        return data
    
    def _clean_personal_info(self, personal: Dict[str, Any]) -> None:
        """Clean personal info section"""
        # Ensure required fields exist
        if "name" not in personal or not personal["name"]:
            personal["name"] = "Unknown"
        
        # Ensure home_address exists and is properly structured
        if "home_address" not in personal or not isinstance(personal["home_address"], dict):
            personal["home_address"] = {"city": None, "state": None, "zip_code": None}
        else:
            address = personal["home_address"]
            for field in ["city", "state", "zip_code"]:
                if field not in address:
                    address[field] = None
        
        # Clean links - ensure they're platform strings
        if "links" not in personal:
            personal["links"] = []
        else:
            cleaned_links = []
            for link in personal["links"]:
                if isinstance(link, dict):
                    if "platform" in link:
                        cleaned_links.append(str(link["platform"]))
                    elif "url" in link:
                        # Determine platform from URL
                        url = str(link["url"]).lower()
                        if "linkedin" in url:
                            cleaned_links.append("linkedin")
                        elif "github" in url:
                            cleaned_links.append("github")
                        elif "instagram" in url:
                            cleaned_links.append("instagram")
                        elif "facebook" in url:
                            cleaned_links.append("facebook")
                        else:
                            cleaned_links.append("other")
                    else:
                        cleaned_links.append("other")
                elif isinstance(link, str):
                    # If it's already a platform string, keep it
                    if link.lower() in ["linkedin", "github", "instagram", "facebook", "handshake", "other"]:
                        cleaned_links.append(link.lower())
                    else:
                        # Try to determine platform from string
                        if "linkedin" in link.lower():
                            cleaned_links.append("linkedin")
                        elif "github" in link.lower():
                            cleaned_links.append("github")
                        else:
                            cleaned_links.append("other")
                else:
                    cleaned_links.append("other")
            personal["links"] = cleaned_links
    
    def _clean_education_item(self, item: Dict[str, Any]) -> None:
        """Clean education item"""
        # Ensure required fields
        if "school_name" not in item:
            item["school_name"] = "Unknown School"
        
        # Ensure degree exists and is properly structured
        if "degree" not in item or not isinstance(item["degree"], dict):
            item["degree"] = {"study": None, "type": "other"}
        else:
            degree = item["degree"]
            if "study" not in degree:
                degree["study"] = None
            if "type" not in degree:
                degree["type"] = "other"
            # Validate degree type
            valid_types = ["high_school", "ged", "bachelors", "masters", "phd", "other_college_level", "other_high_school_level", "other"]
            if degree["type"] not in valid_types:
                degree["type"] = "other"
        
        # Ensure location exists
        if "location" not in item or not isinstance(item["location"], dict):
            item["location"] = {"city": None, "state": None, "zip_code": None}
        else:
            location = item["location"]
            for field in ["city", "state", "zip_code"]:
                if field not in location:
                    location[field] = None
        
        # Clean coursework
        if "relevant_coursework" not in item:
            item["relevant_coursework"] = []
        else:
            item["relevant_coursework"] = self._clean_coursework(item["relevant_coursework"])

        if "skills" not in item:
            item["skills"] = []
        
        # Clean dates
        for date_field in ["start_date", "end_date"]:
            if date_field in item and item[date_field] is not None:
                item[date_field] = self._clean_date(item[date_field])
    
    def _clean_experience_item(self, item: Dict[str, Any]) -> None:
        """Clean experience item"""
        # Ensure type is valid
        if "type" not in item:
            item["type"] = "other"
        else:
            valid_types = ["work", "volunteer", "project", "other"]
            if item["type"] not in valid_types:
                item["type"] = "other"
        
        if "location" not in item or not isinstance(item["location"], dict):
            item["location"] = {"city": None, "state": None, "zip_code": None}
        else:
            location = item["location"]
            for field in ["city", "state", "zip_code"]:
                if field not in location:
                    location[field] = None
        
        if "paragraphs" not in item:
            item["paragraphs"] = []
        else:
            item["paragraphs"] = [str(p) for p in item["paragraphs"] if p and str(p).strip()]
        
        # Ensure links is empty array
        if "links" not in item:
            item["links"] = []
        
        # Clean dates
        for date_field in ["start_date", "end_date"]:
            if date_field in item and item[date_field] is not None:
                item[date_field] = self._clean_date(item[date_field])
    
    def _clean_skill_item(self, skill: Dict[str, Any]) -> None:
        """Clean skill item"""

        if "type" not in skill:
            skill["type"] = "other"
        else:
            valid_types = ["technical", "transferable", "other"]
            if skill["type"] not in valid_types:
                skill["type"] = "other"
        
        if "keywords" not in skill:
            skill["keywords"] = []
        else:
            skill["keywords"] = [str(k) for k in skill["keywords"] if k and str(k).strip()]
    
    def _clean_coursework(self, coursework: List[Any]) -> List[Dict[str, Any]]:
        """Clean coursework list"""
        cleaned = []
        for course in coursework:
            if isinstance(course, dict):
                cleaned_course = {
                    "code": course.get("code"),
                    "name": course.get("name", "Unknown Course")
                }
                cleaned.append(cleaned_course)
            elif isinstance(course, str):
                cleaned.append({"code": None, "name": course})
            else:
                cleaned.append({"code": None, "name": str(course)})
        return cleaned
    
    def _clean_date(self, date_obj: Any) -> Dict[str, Any]:
        """Clean date object"""
        if not isinstance(date_obj, dict):
            return {"year": None, "month": None}
        
        cleaned_date = {}
        
        # Clean year
        if "year" in date_obj and date_obj["year"] is not None:
            try:
                cleaned_date["year"] = int(date_obj["year"])
            except (ValueError, TypeError):
                cleaned_date["year"] = None
        else:
            cleaned_date["year"] = None
        
        # Clean month
        if "month" in date_obj and date_obj["month"] is not None:
            try:
                month = int(date_obj["month"])
                if 1 <= month <= 12:
                    cleaned_date["month"] = month
                else:
                    cleaned_date["month"] = None
            except (ValueError, TypeError):
                cleaned_date["month"] = None
        else:
            cleaned_date["month"] = None
        
        return cleaned_date
    
    def _get_fallback_structure(self, factual: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback structure when LLM fails"""
        return {
            "personal_info": {
                "name": factual.get("personal", {}).get("name", "Unknown"),
                "email": factual.get("personal", {}).get("email"),
                "phone_number": factual.get("personal", {}).get("phone"),
                "home_address": {
                    "city": factual.get("personal", {}).get("address", {}).get("city"),
                    "state": factual.get("personal", {}).get("address", {}).get("state"),
                    "zip_code": factual.get("personal", {}).get("address", {}).get("zip_code")
                },
                "links": []
            },
            "education_items": [],
            "experience_items": [],
            "skills": [],
            "relevant_coursework": [],
            "paragraphs": []
        }