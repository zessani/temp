from fastapi import UploadFile
from app.parser.pipeline1_gemini import Pipeline1Parser
from app.parser.pipeline2.pipeline2_main import Pipeline2Parser

from app.model.schema.resume.education.course import (
    ResumeEducationCourse,
    ResumeEducationCourseCode,
)
from app.model.schema.resume.education.degree import (
    ResumeEducationDegree,
    ResumeEducationDegreeType,
)
from app.model.schema.resume.education.item import ResumeEducationItem
from app.model.schema.resume.experience import (
    ResumeExperienceItem,
    ResumeExperienceType,
)
from app.model.schema.resume.info import ResumePersonalInfo
from app.model.schema.resume.link import ResumeWebLink, ResumeWebLinkPlatform
from app.model.schema.resume.location import ResumeLocation
from app.model.schema.resume.skills import ResumeSkillsList, ResumeSkillsType
from app.model.schema.resume.time import ResumeTimeMonthYear
from app.model.schema.resume.together import Resume


def generate_example_resume() -> Resume:
    return Resume(
        personal_info=ResumePersonalInfo(
            name="John Doe",
            home_address=ResumeLocation(
                city="Tucson",
                state="Arizona",
                zip_code="85732",
            ),
        ),
        education_items=[
            ResumeEducationItem(
                school_name="University of Arizona",
                degree=ResumeEducationDegree(
                    study="Computer Science", type=ResumeEducationDegreeType.BACHELORS
                ),
                gpa=3.82,
                start_date=ResumeTimeMonthYear(year=2022, month=8),
                end_date=None,
                location=ResumeLocation(city="Tucson", state="Arizona"),
                relevant_coursework=[
                    ResumeEducationCourse(
                        code=ResumeEducationCourseCode(prefix="CSC", number="120"),
                        name="Python",
                    ),
                    ResumeEducationCourse(
                        code=ResumeEducationCourseCode(prefix="CSC", number="210"),
                        name="Java",
                    ),
                ],
                skills=[
                    ResumeSkillsList(
                        type=ResumeSkillsType.TECHNICAL,
                        category="Web Development",
                        keywords=["React", "NextJS", "TypeScript", "TailwindCSS"],
                    ),
                    ResumeSkillsList(
                        type=ResumeSkillsType.TECHNICAL,
                        category="Smartphone App Development",
                        keywords=[
                            "Swift",
                            "Kotlin",
                            "Jetpack Compose",
                        ],
                    ),
                    ResumeSkillsList(
                        type=ResumeSkillsType.TRANSFERABLE,
                        category="Leadership Skills",
                        keywords=["Communication", "Writing", "Public Speaking"],
                    ),
                ],
            ),
            ResumeEducationItem(
                school_name="East Side Highschool",
                degree=ResumeEducationDegree(
                    type=ResumeEducationDegreeType.HIGH_SCHOOL
                ),
                gpa=3.45,
                start_date=ResumeTimeMonthYear(year=2018, month=8),
                end_date=ResumeTimeMonthYear(year=2022, month=5),
                location=ResumeLocation(city="Tucson", state="Arizona"),
            ),
        ],
        experience_items=[
            # === WORK IN INDUSTRY ===
            ResumeExperienceItem(
                type=ResumeExperienceType.WORK,
                organization="TechNova Solutions",
                role="Frontend Developer Intern",
                location=ResumeLocation(city="Phoenix", state="Arizona"),
                start_date=ResumeTimeMonthYear(year=2024, month=5),
                end_date=ResumeTimeMonthYear(year=2024, month=8),
                paragraphs=[
                    "Developed and maintained responsive UI components using React and TailwindCSS.",
                    "Worked with a cross-functional team to redesign a customer onboarding dashboard, improving task completion rate by 25%.",
                    "Integrated RESTful APIs using Axios and improved performance by implementing memoization and lazy loading.",
                ],
                links=[
                    ResumeWebLink(
                        url="https://github.com/johndoe/onboarding-dashboard",
                        platform=ResumeWebLinkPlatform.GITHUB,
                    )
                ],
            ),
            ResumeExperienceItem(
                type=ResumeExperienceType.WORK,
                organization="ByteCraft LLC",
                role="Mobile App Developer (Part-Time)",
                location=ResumeLocation(city="Tucson", state="Arizona"),
                start_date=ResumeTimeMonthYear(year=2023, month=9),
                end_date=ResumeTimeMonthYear(year=2024, month=4),
                paragraphs=[
                    "Built cross-platform mobile features using Kotlin (Android) and Swift (iOS) for a fitness tracking app.",
                    "Collaborated with backend team to implement secure user authentication and cloud syncing.",
                    "Reduced app load time by optimizing image rendering and background data fetch routines.",
                ],
                links=[],
            ),
            # === VOLUNTEERING ===
            ResumeExperienceItem(
                type=ResumeExperienceType.VOLUNTEER,
                organization="Tucson Homeless Assistance Center",
                role="Volunteer Software Assistant",
                location=ResumeLocation(city="Tucson", state="Arizona"),
                start_date=ResumeTimeMonthYear(year=2023, month=1),
                end_date=ResumeTimeMonthYear(year=2023, month=12),
                paragraphs=[
                    "Created a small database-driven web app to help track available beds and supply inventory.",
                    "Trained staff on how to use a Google Sheets-based check-in system connected with simple form interfaces.",
                    "Helped modernize intake records and reduce manual errors by over 40%.",
                ],
                links=[],
            ),
            ResumeExperienceItem(
                type=ResumeExperienceType.VOLUNTEER,
                organization="Feeding Arizona",
                role="Event Coordinator & Technical Support",
                location=ResumeLocation(city="Phoenix", state="Arizona"),
                start_date=ResumeTimeMonthYear(year=2022, month=6),
                end_date=ResumeTimeMonthYear(year=2022, month=8),
                paragraphs=[
                    "Managed scheduling and digital signup systems for food distribution events.",
                    "Built an online volunteer scheduling portal using Google Apps Script and Forms.",
                    "Handled basic troubleshooting of on-site equipment and coordinated communication between volunteers.",
                ],
                links=[],
            ),
            # === PERSONAL PROJECTS ===
            ResumeExperienceItem(
                type=ResumeExperienceType.PROJECT,
                organization="Personal",
                role="Creator & Developer",
                location=ResumeLocation(city="Tucson", state="Arizona"),
                start_date=ResumeTimeMonthYear(year=2024, month=2),
                end_date=ResumeTimeMonthYear(year=2024, month=4),
                paragraphs=[
                    "Built 'StudyTrackr', a mobile app to help students schedule and track study sessions with gamification features.",
                    "Developed using Jetpack Compose (Android) and Firebase for real-time sync and authentication.",
                    "Over 500 downloads on GitHub and featured on Reddit's r/learnprogramming.",
                ],
                links=[
                    ResumeWebLink(
                        url="https://github.com/johndoe/studytrackr",
                        platform=ResumeWebLinkPlatform.GITHUB,
                    )
                ],
            ),
            ResumeExperienceItem(
                type=ResumeExperienceType.PROJECT,
                organization="Personal",
                role="Full-Stack Developer",
                location=ResumeLocation(city="Tucson", state="Arizona"),
                start_date=ResumeTimeMonthYear(year=2023, month=7),
                end_date=ResumeTimeMonthYear(year=2023, month=9),
                paragraphs=[
                    "Created a personal budgeting web app with Next.js frontend and Supabase backend.",
                    "Implemented OAuth login, real-time balance updates, and responsive UI using TailwindCSS.",
                    "Integrated currency conversion API and deployed via Vercel.",
                ],
                links=[
                    ResumeWebLink(
                        url="https://github.com/johndoe/budgeteer",
                        platform=ResumeWebLinkPlatform.GITHUB,
                    )
                ],
            ),
        ],
        paragraphs=[
            "Hello, my name is John. This is my self-introduction. I am an experienced professional in software development..."
        ],
    )


# Put the resume-parsing logic here.
# def parse_resume(file: UploadFile) -> Resume:
#    return generate_example_resume()

parser = Pipeline1Parser()

# REPLACE THIS FUNCTION with Pipeline 1
async def parse_resume(file: UploadFile) -> Resume:
    result = await parser.parse_resume(file)
    print(f"Pipeline 1 - Cost: ${result.cost_estimate:.4f}, Tokens: {result.tokens_used}")
    return result.resume
