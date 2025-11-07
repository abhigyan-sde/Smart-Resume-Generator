from langchain_openai import ChatOpenAI
from langchain.prompts import (ChatPromptTemplate, SystemMessagePromptTemplate,
                                HumanMessagePromptTemplate, AIMessagePromptTemplate)
from app.models.job_models import JobDescriptionDocument
from app.services.skill_extractor import SkillExtractor
from typing import Any, Dict
from textwrap import dedent


class JobParser:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    jobParserLLM = llm.with_structured_output(JobDescriptionDocument, method="function_calling")

    @staticmethod
    def _build_prompt() -> ChatPromptTemplate:
        """
        Builds a structured ChatPromptTemplate for job posting parsing.
        Placeholders:
            - {job_text}
        """
        system_message = SystemMessagePromptTemplate.from_template(dedent("""\
            You are an expert job posting parser.
            Your task is to extract structured fields from job postings and output JSON 
            that strictly follows the JobDescriptionDocument schema:

            JobDescriptionDocument {
                title: string | null,
                company: string | null,
                location: string | null,

                responsibilities: array<string>,       # “What you'll do”
                qualifications: array<string>,         # Education + generic reqs
                technical_skills: array<string>,       # Raw extracted skills/tools

                role: string | null,                 # e.g., "Software Engineer"
                seniority: string | null,            # e.g., "Mid", "Senior"
                domain: array<string>,                 # e.g., ["Backend", "Platform"]

                must_have_skills: array<string>,       # subset of technical_skills
                nice_to_have_skills: array<string>,    # subset of technical_skills

                years_experience_min: float | null,
                years_experience_pref: float | null,
                education_required: string | null,   # e.g., "BS in CS or related"

                normalized_skills: map<string, array<string>>,
                priority_weights: map<string, float>,

                source_url: string | null,
                raw_text: string | null
            }

            Rules:
            - Extract values exactly from the job posting; do not hallucinate or paraphrase.
            - responsibilities, qualifications, and technical_skills must be sets of strings (deduplicated).
            - Extract technical_skills from responsibilities, qualifications, and explicit skills sections.
            - Normalize skills to lowercase and deduplicate when filling technical_skills.
            - Infer role, seniority, and domain if mentioned in the posting.
            - years_experience_min and years_experience_pref must be numeric if possible.
            - If a field is not specified, set it to null (for scalars) or an empty set/dict (for collections).
            - The final output must be valid JSON conforming exactly to the schema.
            - Do not include any commentary or text outside the JSON.
            """))

        human_message = HumanMessagePromptTemplate.from_template(dedent("""\
            Here is the job posting text:

            {job_text}
            """))

        ai_message = AIMessagePromptTemplate.from_template(dedent("""\
            Stepwise extraction plan:
            1. Extract title, company, and location if present.
            2. Identify responsibilities, qualifications, and technical_skills as sets of strings.
            3. Detect must_have_skills and nice_to_have_skills if explicitly mentioned.
            4. Extract role, seniority, and domain (backend, frontend, platform, etc.) if available.
            5. Parse years of experience requirements into years_experience_min and years_experience_pref.
            6. Capture education_required if explicitly stated.
            7. Aggregate all technical skills, deduplicated and in lowercase.
            8. Validate JSON types and ensure all required fields exist, filling with defaults where missing.
            9. Assemble the final JSON object strictly following JobDescriptionDocument.

            Return only the JSON output.
            """))

        return ChatPromptTemplate.from_messages(
            [system_message, human_message, ai_message]
        )

    @staticmethod
    def parse_job_posting(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse job description into structured model.
        Accepts either:
        1. job_text: the JD text directly, or
        2. url: a URL to fetch the JD from (will fail gracefully for blocked domains)
        """
        print("begin job Parser")
        job_text = state["job_text"]

        prompt = JobParser._build_prompt()
        formatted_prompt = prompt.format(job_text=job_text)

        chain = formatted_prompt | JobParser.jobParserLLM
        job_data : JobDescriptionDocument = chain.invoke({"job_text": job_text})
    
        # --- Skill Normalization ---
        extracted_skills = set(job_data.technical_skills or [])
        normalized_skills = SkillExtractor.normalize(extracted_skills)
        job_data.normalized_skills = normalized_skills
        job_data.priority_weights = {skill: 1.0 for skill in normalized_skills}
        
        job_data.raw_text = job_text

        print("end job parser")
        print("parsed job req : ", job_data)
        state["job_description_doc"] = job_data
        return state