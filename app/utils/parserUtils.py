import re
from app.models.resume import ResumeSection, ResumeEntry
from typing import List, Optional

SECTION_KEYWORDS = {
    "summary": ["summary", "objective", "professional summary"],
    "work_experience": ["experience", "work", "employment", "career history"],
    "education": ["education", "academics", "qualifications"],
    "projects": ["projects", "academic projects", "personal projects"],
    "hobbies": ["hobbies", "interests", "activities"],
}

EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_REGEX = re.compile(r"(\+\d{1,3}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}")
LINKEDIN_REGEX = re.compile(r"(linkedin\.com/\S+)")
GITHUB_REGEX = re.compile(r"(github\.com/\S+)")

class ParserUtils:

    @staticmethod
    def detect_personal_info(entries: list[ResumeEntry]) -> list[ResumeEntry]:
        """Extract name/email/phone/linkedin/github from top entries."""
        personal_entries = []
        for entry in entries[:10]:  # only scan first few lines
            if EMAIL_REGEX.search(entry.content) or PHONE_REGEX.search(entry.content) \
               or LINKEDIN_REGEX.search(entry.content) or GITHUB_REGEX.search(entry.content):
                personal_entries.append(entry)
        return personal_entries

    @staticmethod
    def detect_sections(entries: list[ResumeEntry]) -> list[ResumeSection]:
        """Split entries into sections based on keywords and formatting."""
        sections: list[ResumeSection] = []
        current_section = ResumeSection(
            header=ResumeEntry(id="header_uncategorized", content="Uncategorized"),
            order=0,
            entries=[]
        )

        def flush_section():
            if current_section.entries:
                sections.append(current_section)

        order_counter = 1
        for entry in entries:
            normalized = entry.content.strip().lower()
            matched_section = None
            for sec_name, keywords in SECTION_KEYWORDS.items():
                if any(k in normalized for k in keywords):
                    matched_section = sec_name
                    break

            if matched_section:
                flush_section()
                current_section = ResumeSection(
                    header=entry,
                    order=order_counter,
                    entries=[]
                )
                order_counter += 1
            else:
                current_section.entries.append(entry)

        flush_section()
        return sections

    @staticmethod
    def build_resume_sections(entries: List[ResumeEntry]) -> List[ResumeSection]:
        """Main orchestrator: detects personal info + other sections."""
        sections = []
        personal_section = ParserUtils.detect_personal_info(entries)
        if personal_section:
            sections.append(personal_section)

        other_sections = ParserUtils.detect_sections(entries)
        sections.extend(other_sections)
        return sections