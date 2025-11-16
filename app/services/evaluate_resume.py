from app.prompts.resume_evaluation_prompt import build_resume_evaluation_prompt
from app.models.resume_feedback import ResumeEvaluationResult
from langchain_openai import ChatOpenAI

async def evaluate_resume_against_jd(resume_text: str, job_description: str) -> ResumeEvaluationResult:

    prompt = build_resume_evaluation_prompt(resume_text, job_description)

    llm = ChatOpenAI(
        model="gpt-40-mini",
        temperature=0.2
    )

    # Call the LLM
    response = await llm.invoke(prompt)

    raw_output = response.content

    # Validate JSON response using Pydantic
    try:
        parsed = ResumeEvaluationResult.model_validate_json(raw_output)
    except Exception as e:
        raise ValueError(
            f"Failed to parse LLM output into ResumeEvaluationResult: {e}\n\nLLM Output:\n{raw_output}"
        )

    return parsed
