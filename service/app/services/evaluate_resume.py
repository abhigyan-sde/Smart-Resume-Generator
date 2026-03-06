from app.prompts.resume_evaluation_prompt import build_resume_evaluation_prompt
from app.models.resume_feedback import ResumeEvaluationResult
from langchain_openai import ChatOpenAI


async def evaluate_resume_against_jd(resume_text: str, job_description: str) -> ResumeEvaluationResult:
    try:
        prompt = build_resume_evaluation_prompt(resume_text, job_description)
        print("************************ PROMPT *****************")
        print(prompt)

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        response = await llm.ainvoke(prompt)

        # Type-safe extraction
        if isinstance(response.content, str): # type: ignore
            raw_output = response.content
        else:
            import json
            raw_output = json.dumps(response.content)# type: ignore

        print("****************LLM OUTPUT****************")
        print(raw_output)

        # Parse JSON into Pydantic model
        try:
            parsed = ResumeEvaluationResult.model_validate_json(raw_output)
        except Exception as e:
            raise ValueError(
                f"Failed to parse LLM output into ResumeEvaluationResult: {e}\n\nLLM Output:\n{raw_output}"
            )

        return parsed

    except Exception as e:
        print(f"[ERROR] {e}")
        raise ValueError(e)
