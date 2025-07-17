import google.generativeai as genai
import json
from typing import Dict

from app.config.env_vars import EnvironmentVars


class Pipeline2Extractors:
    def __init__(self):
        genai.configure(api_key=EnvironmentVars.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def extract_facts(self, text: str) -> Dict:
        """Extract comprehensive factual information (temp=0.0)"""
        prompt = f"""Extract ALL factual information exactly as written. Be comprehensive and detailed.

Extract:
1. PERSONAL INFO:
   - Full name, email, phone (exact format)
   - Address, city, state, zip
   - Links (LinkedIn, GitHub, portfolio URLs)

2. EDUCATION:
   - School names (exact, full official names)
   - Degree types and fields of study (complete descriptions)
   - GPAs (exact numbers)
   - Dates (exact: "Aug 2023 - May 2027")
   - Locations (city, state)
   - ALL coursework mentioned (exact names)

3. EXPERIENCE & PROJECTS:
   - ALL organization names (exact, full names)
   - ALL job titles/roles (exact as written)
   - ALL dates (exact format)
   - ALL locations (city, state)
   - ALL bullet points and descriptions (word-for-word)
   - ALL achievements and metrics mentioned

4. SKILLS:
   - ALL technical skills mentioned anywhere
   - ALL soft skills mentioned anywhere
   - ALL tools, languages, frameworks

Return comprehensive JSON:
{{
  "personal": {{
    "name": "Exact Full Name",
    "email": "email@domain.com",
    "phone": "phone number",
    "address": "full address",
    "links": ["linkedin.com/in/username", "github.com/username", "portfolio.com"]
  }},
  "education": [
    {{
      "school": "Full University Name",
      "degree": "Complete Degree Description with Minor",
      "gpa": 3.5,
      "dates": "Aug 2023 - May 2027",
      "location": "City, State",
      "coursework": ["Course Name 1", "Course Name 2", "Course Name 3"]
    }}
  ],
  "experiences": [
    {{
      "organization": "Full Organization Name",
      "role": "Exact Job Title",
      "dates": "Sep 2024 - Present",
      "location": "City, State",
      "bullets": ["Bullet point 1 word for word", "Bullet point 2 word for word"]
    }}
  ],
  "skills": {{
    "technical": ["Python", "JavaScript", "React"],
    "soft": ["Leadership", "Communication"],
    "tools": ["Docker", "Git", "AWS"]
  }}
}}

Text: {text}"""
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=4096,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    
    def recognize_patterns(self, text: str, factual_data: Dict) -> Dict:
        """Recognize patterns and enhance categorization (temp=0.1)"""
        prompt = f"""Using the factual data and original text, systematically categorize and enhance the information.

CATEGORIZATION RULES:
1. Experience types:
   - "work": Paid jobs, internships, research positions, leadership roles, medical shadowing, fellowships
   - "project": Personal projects, hackathons, course projects, individual pathways
   - "volunteer": Unpaid community service, religious organizations

2. Education levels:
   - "bachelors", "masters", "phd", "high_school"

3. Skill categories:
   - "technical": Programming languages, frameworks, tools, databases, cloud services
   - "transferable": Communication, leadership, teamwork, problem-solving

4. Link platforms:
   - Identify: "linkedin", "github", "instagram", "facebook", "other"

5. Date parsing:
   - "Sep 2024 - Present" → start: {{year: 2024, month: 9}}, end: null
   - "Aug 2023 - May 2027" → start: {{year: 2023, month: 8}}, end: {{year: 2027, month: 5}}

Factual data: {json.dumps(factual_data)}

Return enhanced categorization:
{{
  "experience_categorization": [
    {{
      "organization": "Company Name",
      "role": "Job Title",
      "type": "work",
      "start_date": {{"year": 2024, "month": 9}},
      "end_date": null,
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
      "coursework": ["Course 1", "Course 2"]
    }}
  ],
  "skills_categorization": [
    {{"type": "technical", "category": "Programming Languages", "skills": ["Python", "Java"]}},
    {{"type": "technical", "category": "Frameworks", "skills": ["React", "Next.js"]}},
    {{"type": "transferable", "category": "Leadership", "skills": ["Communication", "Teamwork"]}}
  ],
  "links_categorization": [
    {{"url": "linkedin.com/in/username", "platform": "linkedin"}},
    {{"url": "github.com/username", "platform": "github"}}
  ]
}}

Original text: {text}"""
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)