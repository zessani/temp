import google.generativeai as genai
import json
from typing import Dict, List, Any

from app.config.env_vars import EnvironmentVars


class Pipeline2Extractors:
    def __init__(self):
        genai.configure(api_key=EnvironmentVars.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def extract_facts(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive factual information (temp=0.0)"""
        prompt = f"""Extract ALL factual information exactly as written from this resume. Be comprehensive and detailed.

EXTRACT EVERYTHING:
1. PERSONAL INFO:
   - Full name (exact as written)
   - Email address (exact format)
   - Phone number (exact format)
   - Home address (complete address if available)
   - All links and URLs (LinkedIn, GitHub, portfolio, etc.)

2. EDUCATION:
   - School names (exact, full official names)
   - Degree types and fields of study (complete descriptions including majors/minors)
   - GPAs (exact numbers with decimal places)
   - Dates (exact format as written: "Aug 2023 - May 2027", "2023-present", etc.)
   - Locations (city, state if mentioned)
   - ALL coursework mentioned (exact course names and codes if available)

3. EXPERIENCE & PROJECTS:
   - ALL organization/company names (exact, full names)
   - ALL job titles/roles (exact as written)
   - ALL dates (exact format as written)
   - ALL locations (city, state if mentioned)
   - ALL bullet points and descriptions (word-for-word, preserve formatting)
   - ALL achievements, metrics, and quantifiable results
   - ALL project names and descriptions

4. SKILLS:
   - ALL technical skills mentioned anywhere in the resume
   - ALL soft skills mentioned anywhere
   - ALL tools, languages, frameworks, platforms, databases
   - ALL certifications or technical proficiencies

5. ADDITIONAL SECTIONS:
   - Awards, honors, certifications
   - Publications, research
   - Languages spoken
   - Any other relevant information

Return comprehensive JSON with this exact structure:
{{
  "personal": {{
    "name": "Full Name As Written",
    "email": "email@domain.com",
    "phone": "phone number with formatting",
    "address": {{
      "full_address": "complete address if available",
      "city": "city name",
      "state": "state name",
      "zip_code": "zip code if available"
    }},
    "links": [
      {{
        "url": "https://linkedin.com/in/username",
        "text": "text as it appears on resume"
      }},
      {{
        "url": "https://github.com/username",
        "text": "text as it appears on resume"
      }}
    ]
  }},
  "education": [
    {{
      "school": "Full University Name",
      "degree": "Complete Degree Description with Major/Minor",
      "gpa": 3.50,
      "dates": "Aug 2023 - May 2027",
      "location": {{
        "city": "City Name",
        "state": "State Name"
      }},
      "coursework": [
        {{
          "code": "CSC 120",
          "name": "Introduction to Programming"
        }},
        {{
          "code": null,
          "name": "Data Structures"
        }}
      ]
    }}
  ],
  "experiences": [
    {{
      "organization": "Full Organization Name",
      "role": "Exact Job Title",
      "dates": "Sep 2024 - Present",
      "location": {{
        "city": "City Name",
        "state": "State Name"
      }},
      "bullets": [
        "Complete bullet point 1 exactly as written",
        "Complete bullet point 2 exactly as written",
        "Complete bullet point 3 exactly as written"
      ],
      "type_hints": "work/project/volunteer based on context"
    }}
  ],
  "skills": {{
    "technical": [
      {{
        "category": "Programming Languages",
        "items": ["Python", "JavaScript", "Java"]
      }},
      {{
        "category": "Frameworks",
        "items": ["React", "Node.js", "Express"]
      }},
      {{
        "category": "Tools",
        "items": ["Git", "Docker", "AWS"]
      }}
    ],
    "soft": [
      {{
        "category": "Leadership",
        "items": ["Team Leadership", "Project Management"]
      }},
      {{
        "category": "Communication",
        "items": ["Public Speaking", "Technical Writing"]
      }}
    ]
  }},
  "additional": {{
    "awards": ["Award Name 1", "Award Name 2"],
    "certifications": ["Certification 1", "Certification 2"],
    "languages": ["English (Native)", "Spanish (Conversational)"],
    "other": ["Any other relevant information"]
  }}
}}

CRITICAL INSTRUCTIONS:
- Extract EVERYTHING mentioned in the resume
- Preserve exact wording and formatting
- Do not interpret or modify the content
- Include all bullet points completely
- Include all coursework mentioned
- Include all skills mentioned anywhere
- Include all dates exactly as written
- Include all organization names exactly as written

Resume Text:
{text}"""
        
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
            print(f"Error in extract_facts: {e}")
            return self._get_empty_factual_structure()
    
    def recognize_patterns(self, text: str, factual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize patterns and enhance categorization (temp=0.1)"""
        prompt = f"""Using the factual data extracted from the resume, categorize and structure the information according to the resume schema requirements.

CATEGORIZATION RULES:
1. Experience Types:
   - "work": Paid jobs, internships, research positions, teaching positions, leadership roles, medical shadowing, fellowships, co-ops
   - "project": Personal projects, hackathons, course projects, individual research, startup projects, open source contributions
   - "volunteer": Unpaid community service, religious organizations, nonprofit work, pro bono work

2. Education Levels:
   - "high_school": High school diploma, GED
   - "bachelors": Bachelor's degree, BS, BA, B.Eng, etc.
   - "masters": Master's degree, MS, MA, MBA, M.Eng, etc.
   - "phd": PhD, Doctorate, Ed.D, etc.

3. Skill Categories:
   - "technical": Programming languages, frameworks, tools, databases, cloud services, software, hardware
   - "transferable": Communication, leadership, teamwork, problem-solving, time management, adaptability

4. Link Platforms:
   - "linkedin": LinkedIn profiles
   - "github": GitHub profiles
   - "instagram": Instagram profiles
   - "facebook": Facebook profiles
   - "other": All other links

5. Date Parsing Examples:
   - "Sep 2024 - Present" → start: {{"year": 2024, "month": 9}}, end: null
   - "Aug 2023 - May 2027" → start: {{"year": 2023, "month": 8}}, end: {{"year": 2027, "month": 5}}
   - "2023-2024" → start: {{"year": 2023, "month": null}}, end: {{"year": 2024, "month": null}}
   - "2023-present" → start: {{"year": 2023, "month": null}}, end: null

Factual Data: {json.dumps(factual_data, indent=2)}

Return enhanced categorization with this exact structure:
{{
  "experience_categorization": [
    {{
      "organization": "Company Name",
      "role": "Job Title",
      "type": "work",
      "start_date": {{"year": 2024, "month": 9}},
      "end_date": null,
      "location": {{"city": "City", "state": "State"}},
      "bullets": ["Detailed bullet point 1", "Detailed bullet point 2"]
    }}
  ],
  "education_categorization": [
    {{
      "school": "University Name",
      "degree_type": "bachelors",
      "degree_study": "Computer Science",
      "gpa": 3.5,
      "start_date": {{"year": 2023, "month": 8}},
      "end_date": {{"year": 2027, "month": 5}},
      "location": {{"city": "City", "state": "State"}},
      "coursework": [
        {{"code": "CSC 120", "name": "Introduction to Programming"}},
        {{"code": null, "name": "Data Structures"}}
      ]
    }}
  ],
  "skills_categorization": [
    {{"type": "technical", "category": "Programming Languages", "skills": ["Python", "Java"]}},
    {{"type": "technical", "category": "Frameworks", "skills": ["React", "Next.js"]}},
    {{"type": "transferable", "category": "Leadership", "skills": ["Communication", "Teamwork"]}}
  ],
  "links_categorization": [
    {{"url": "https://linkedin.com/in/username", "platform": "linkedin"}},
    {{"url": "https://github.com/username", "platform": "github"}}
  ],
  "personal_categorization": {{
    "name": "Full Name",
    "email": "email@domain.com",
    "phone": "phone number",
    "address": {{"city": "City", "state": "State", "zip_code": null}}
  }}
}}

CRITICAL INSTRUCTIONS:
- Use the factual data as the source of truth
- Categorize based on context and common sense
- Preserve all bullet points in their entirety
- Parse dates carefully according to the examples
- Ensure all information is preserved during categorization
- Don't lose any details during the categorization process

Original Resume Text for Context:
{text}"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in recognize_patterns: {e}")
            return self._get_empty_pattern_structure()
    
    def _get_empty_factual_structure(self) -> Dict[str, Any]:
        """Return empty factual structure for error handling"""
        return {
            "personal": {
                "name": "",
                "email": None,
                "phone": None,
                "address": {"full_address": None, "city": None, "state": None, "zip_code": None},
                "links": []
            },
            "education": [],
            "experiences": [],
            "skills": {"technical": [], "soft": []},
            "additional": {"awards": [], "certifications": [], "languages": [], "other": []}
        }
    
    def _get_empty_pattern_structure(self) -> Dict[str, Any]:
        """Return empty pattern structure for error handling"""
        return {
            "experience_categorization": [],
            "education_categorization": [],
            "skills_categorization": [],
            "links_categorization": [],
            "personal_categorization": {
                "name": "",
                "email": None,
                "phone": None,
                "address": {"city": None, "state": None, "zip_code": None}
            }
        }