import re
from typing import Dict


def parse_resume_sections(text: str) -> Dict[str, str]:
    """Split resume text into different sections."""
    text = re.sub(r'\s+', ' ', text.strip())
    
    sections = {}
    sections['personal'] = get_contact_info(text)
    sections['education'] = find_education_section(text)
    sections['work'] = find_work_section(text)  
    sections['volunteer'] = find_volunteer_section(text)
    sections['skills'] = find_skills_section(text)
    sections['projects'] = find_projects_section(text)
    
    return sections


def get_contact_info(text: str) -> str:
    lines = text.split('\n')
 
    section_headers = ['EDUCATION', 'EXPERIENCE', 'WORK', 'SKILLS', 'PROJECTS', 'VOLUNTEER']
    
    contact_lines = []
    for i, line in enumerate(lines):
        line_upper = line.strip().upper()
        if any(header in line_upper for header in section_headers):
            break
        if i >= 10:
            break
            
        contact_lines.append(line)
    return '\n'.join(contact_lines)


def find_education_section(text: str) -> str:
    headers = ['EDUCATION', 'ACADEMIC', 'SCHOOL']
    return find_section_with_headers(text, headers)


def find_work_section(text: str) -> str:
    headers = ['EXPERIENCE', 'WORK', 'EMPLOYMENT', 'PROFESSIONAL']
    return find_section_with_headers(text, headers)


def find_volunteer_section(text: str) -> str:
    headers = ['VOLUNTEER', 'COMMUNITY', 'SERVICE']
    return find_section_with_headers(text, headers)


def find_skills_section(text: str) -> str:
    headers = ['SKILLS', 'TECHNICAL', 'TECHNOLOGIES']
    return find_section_with_headers(text, headers)


def find_projects_section(text: str) -> str:
    headers = ['PROJECTS', 'PROJECT', 'PORTFOLIO']
    return find_section_with_headers(text, headers)


def find_section_with_headers(text: str, headers: list) -> str:
    
    for header in headers:
        content = get_section_content(text, header)
        if content:
            return content
    
    return ""


def get_section_content(text: str, header: str) -> str:
    
    start = re.search(header, text, re.IGNORECASE)
    if not start:
        return ""
    
    start_pos = start.start()
    
    all_headers = ['EDUCATION', 'EXPERIENCE', 'WORK', 'SKILLS', 'PROJECTS', 'VOLUNTEER', 'COMMUNITY']
    end_pos = len(text)
    
    for next_header in all_headers:
        if next_header.lower() != header.lower():
            next_section = re.search(next_header, text[start_pos + 10:], re.IGNORECASE)
            if next_section:
                new_end = start_pos + 10 + next_section.start()
                if new_end < end_pos:
                    end_pos = new_end
    
    content = text[start_pos:end_pos].strip()
    return content












# Test case
if __name__ == "__main__":
    test_resume = """
    John Doe
    john@email.com | (555) 123-4567
    123 Main St, City, State
    
    EDUCATION
    University of Arizona
    Bachelor of Science in Computer Science
    GPA: 3.5, Aug 2023 - May 2027
    
    SKILLS
    Python, JavaScript, React, MongoDB
    Problem-solving, Communication
    
    EXPERIENCE
    Software Developer at Tech Company
    June 2024 - Present
    Built web applications using React and Node.js
    
    PROJECTS
    Resume Parser Project
    Built an AI-powered resume parsing system
    """
    
    # Test the parser
    sections = parse_resume_sections(test_resume)
    
    print("=== PARSED SECTIONS ===")
    for section_name, content in sections.items():
        print(f"\n{section_name.upper()}:")
        print("-" * 20)
        print(content[:200] + "..." if len(content) > 200 else content)