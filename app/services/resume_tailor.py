# app/services/tailoring_service.py
from typing import Dict, Any, List, Set
from app.models.resume_models import ResumeDocument, ResumeEntry, Section, ResumeMetadata
from app.models.job_models import JobDescriptionDocument
from langchain_openai import ChatOpenAI
from app.services.skill_extractor import SkillExtractor
import json
from textwrap import dedent
from langchain.prompts import (ChatPromptTemplate, AIMessagePromptTemplate,
                               SystemMessagePromptTemplate, HumanMessagePromptTemplate)

class TailoringService:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    @staticmethod
    def build_refactor_prompt(entries_by_section: Dict[str, List[ResumeEntry]], 
                              missing_skills: Set[str], metadata: ResumeMetadata) -> ChatPromptTemplate:
        """
        Constructs a ChatPromptTemplate for tailoring (refactoring) resume entries
        to include missing technical skills while preserving formatting and structure.
        """

        # Serialize inputs
        sections_json = {
            section: [entry.model_dump() for entry in entries]
            for section, entries in entries_by_section.items()
        }

        # -----------------------------
        # System Message
        # -----------------------------
        system_message = SystemMessagePromptTemplate.from_template(dedent("""\
            You are an expert resume tailoring assistant.
            Your task is to refactor existing resume entries to naturally incorporate missing technical skills,
            while strictly preserving structure, metadata, and meaning.

            ResumeEntry schema {
                id: string,              # Must remain unchanged
                content: string,         # May be updated to include missing skills
                font: string | null,
                font_size: string | null,
                font_color: string | null,
                bold: boolean,
                italic: boolean,
                bullet: boolean,
                bullet_symbol: string | null,
                technical_skills: Set<string>
            }

            Rules:
            - Only update the content and technical_skills when                                                          
            - Do NOT invent new experiences, jobs, or projects.
            - Insert missing skills naturally into existing content where relevant.
            - Preserve all metadata (font, bold, italic, bullet, bullet_symbol).
            - Maintain section grouping and entry order.
            - Do not modify the unique identifier (id).
            - The final output must be valid JSON in the format:
                {
                    "section_name_1": [ResumeEntry, ResumeEntry, ...],
                    "section_name_2": [ResumeEntry, ...]
                }
            """))

        # -----------------------------
        # Human Message
        # -----------------------------
        human_message = HumanMessagePromptTemplate.from_template(dedent(f"""\
            Missing Skills: {list(missing_skills)}

            Resume Metadata:
            {metadata.model_dump()}

            Entries to Refactor (grouped by section):
            {json.dumps(sections_json, indent=2)}
        """))

        # -----------------------------
        # AI Message (stepwise reasoning)
        # -----------------------------
        ai_message = AIMessagePromptTemplate.from_template(dedent("""\
            Stepwise tailoring plan:
            1. Review missing skills list and identify relevant sections/entries where they could fit.
            2. Insert missing skills into the most natural entries without exaggeration.
            3. Ensure all original metadata (font, bold, italic, bullets, bullet symbols) is preserved.
            4. Keep section order and entry order unchanged.
            5. Do not alter entry IDs.
            6. Update technical_skills field of each ResumeEntry to include newly added skills.
            7. Produce JSON grouped by section, strictly matching the required format.

            Return only the final JSON object.
        """))

        # -----------------------------
        # Assemble ChatPromptTemplate
        # -----------------------------
        return ChatPromptTemplate.from_messages(
            [system_message, human_message, ai_message]
        )


    @staticmethod
    def apply_refactored_entries(resume: ResumeDocument, llm_output: str) -> ResumeDocument:
        """
        Apply the refactored entries returned by LLM back into the ResumeDocument.
        Only updates entries for existing sections. Any new sections or new entries 
        in the LLM output are ignored.

        Expects LLM output in the format:
        {
            "Work Experience": [ResumeEntry_dict, ...],
            "Projects": [ResumeEntry_dict, ...],
            ...
        }

        Each ResumeEntry_dict should contain an 'id' field that matches an existing ResumeEntry.
        """
        print("begin resume refactoring")
        try:
            refactored_sections: Dict[str, List[Dict]] = json.loads(llm_output)
        except Exception as e:
            raise ValueError(f"Invalid JSON from LLM: {str(e)}")

        updated_sections: List[Section] = []

        for section in resume.sections:
            section_name = section.header.content
            original_entries_map = {entry.id: entry for entry in section.entries}

            if section_name in refactored_sections:
                updated_entries: List[ResumeEntry] = []
                for entry_dict in refactored_sections[section_name]:
                    entry_id = entry_dict.get("id")
                    if entry_id in original_entries_map:
                        # Merge original metadata with refactored content
                        original_entry = original_entries_map[entry_id]
                        merged_entry = ResumeEntry(**{**original_entry.model_dump(), **entry_dict})
                        updated_entries.append(merged_entry)
                    # Ignore any entries that do not match existing IDs

                # Preserve original order
                updated_entries.sort(
                    key=lambda x: next((i for i, e in enumerate(section.entries) if e.id == x.id))
                )

                updated_sections.append(
                    Section(
                        header=section.header,
                        order=section.order,
                        entries=updated_entries
                    )
                )
            else:
                # Keep section unchanged
                updated_sections.append(section)

        print("end resume refactoring")
        return ResumeDocument(
            sections=updated_sections,
            metadata=resume.metadata  # Metadata remains unchanged
        )

    @staticmethod
    def tailor_resume(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node for tailoring the resume based on job requirements.
        """
        print("begin resume tailoring")
        resume: ResumeDocument = state["structured_resume_doc"]
        job: JobDescriptionDocument = state["job_description_doc"]

        # Normalize resume skills
        resume_normalized_skills = SkillExtractor.normalize(resume.all_skills)
        must_have_normalized_skills = SkillExtractor.normalize(job.must_have_skills)
        # Determine missing must-have skills
        missing_skills = must_have_normalized_skills.keys() - resume_normalized_skills.keys()
        if not missing_skills:
            # Nothing to refactor
            state["resume_doc"] = resume
            return state

        candidates = {
            section.header.content: section.entries
            for section in resume.sections
            if section.header.content in ["Work Experience", "Projects", "Technical Skills"]
        }

        # Build LLM prompt
        prompt = TailoringService.build_refactor_prompt(candidates, missing_skills, resume.metadata)
        # Invoke LLM
        chain = prompt | TailoringService.llm
        response = chain.invoke({})
        updated_entries_json = response.content

        # Apply refactored entries
        TailoringService.apply_refactored_entries(resume, updated_entries_json)
        print("end resume tailoring")
        print("tailored resume : ", resume)
        # Update state
        state["resume_tailored_doc"] = resume
        return state
