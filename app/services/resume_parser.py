from typing import Dict, Any
from app.models.resume_models import ResumeDocument
from langchain_openai import ChatOpenAI
from app.services.skill_extractor import SkillExtractor
from langchain.prompts import (AIMessagePromptTemplate, ChatPromptTemplate, 
                               SystemMessagePromptTemplate, HumanMessagePromptTemplate)
from textwrap import dedent

class ResumeParser:
    # LLM instance (gpt-4o-mini recommended for structured output)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser_llm = llm.with_structured_output(ResumeDocument, method="function_calling")

    @staticmethod
    def _build_prompt() -> ChatPromptTemplate:
        """
        Returns a ChatPromptTemplate with placeholders:
        - {filename}
        - {file_data}
        Format the template at call-time with prompt_template.format(...) or format_prompt(...)
        """
        system_message = SystemMessagePromptTemplate.from_template(dedent("""\
            You are an expert resume parser.
            Your task is to parse resumes accurately and output JSON that strictly follows the ResumeDocument schema as defined below.

            ResumeDocument {
                sections: List<Section> {
                    header: ResumeEntry,
                    order: int,
                    entries: List<ResumeEntry>
                },
                metadata: ResumeMetadata {
                    border: boolean,
                    columns: int,
                    entry_per_column: int,
                    pages: int,
                    alignment: str,
                    inter_section_spaces: int,
                    inter_entry_spaces: int
                },
                all_skills: array<string>
            }

            ResumeEntry {
                content: string,
                font: string | null,
                font_size: string | null,
                font_color: string | null,
                bold: boolean,
                italic: boolean,
                bullet: boolean,
                bullet_symbol: string | null,
                technical_skills: array<string>
            }

            Rules:
            - Each line in the resume should be captured as a ResumeEntry object (one ResumeEntry per line).
            - Use arrays (JSON lists) for collections (e.g., technical_skills, all_skills).
            - all_skills must be the deduplicated, lowercase union of all technical skills across entries.
            - Technical skills include programming languages, frameworks, libraries, tools, platforms, and cloud services.
            - Defaults: alignment = "left" if unknown, border = false if not detected, pages = 1 if unknown.
            - Maintain original order of sections and entries. The 'order' field must reflect sequence in the document.
            - If a metadata item cannot be determined, use null (or the provided defaults).

            IMPORTANT:
            - Do not hallucinate or change any text content.
            - The final output must be valid JSON that conforms exactly to the schema above.
            - Use arrays for sets (e.g., all_skills -> ["python","sql"]).
            - Do not include any explanation or extra text outside the JSON.
        """))

        human_message = HumanMessagePromptTemplate.from_template(dedent("""\
            I will provide the text of a resume extracted from a file ({filename}).
            Your goal is to extract structured resume data step by step.

            RESUME TEXT:
            {file_data}
        """))

        ai_message = AIMessagePromptTemplate.from_template(dedent("""\
            Stepwise instructions:
            1) Identify all sections (Personal Info, Summary, Education, Work Experience, Projects, Technical Skills, etc.).
            2) For each section, extract entries (one ResumeEntry per line) and detect formatting metadata when present.
            3) Extract technical skills per entry and list them under technical_skills (lowercase).
            4) Compute ResumeMetadata (border, columns, entry_per_column, pages, alignment, inter-section and inter-entry spacing).
            5) Aggregate all_skills as the deduplicated, lowercase array of skills.
            6) Validate JSON types: ints for counts, booleans for flags, arrays for lists, null where unknown.
            7) Final step: verify that the assembled JSON strictly follows the ResumeDocument schema above.

            Return only the JSON — no extra text. Arrays (not Sets) must be used for list-like fields.
        """))

        return ChatPromptTemplate.from_messages([system_message, human_message, ai_message])


    @staticmethod
    def parse_resume(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node: Sends the uploaded file to the LLM for parsing into ResumeDocument.
        """
        print("Begin resume parser")
        file_data = state["resume"]
        filename = state["filename"]
        prompt = ResumeParser._build_prompt()
        prompt_formatted = prompt.format(filename=filename, file_data = file_data)
        structured_resume: ResumeDocument = ResumeParser.parser_llm.invoke(prompt_formatted)
        structured_resume.normalized_skills = SkillExtractor.normalize(structured_resume.all_skills)
        print("Structured Resume : ", structured_resume)
        print("end resume parser")
        state["structured_resume_doc"] = structured_resume
        return state