import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app.services.orchestrator import OrchestratorService


def test_orchestrator():
    with open("tests/sample_resumes/resume.pdf", "rb") as f:
        pdf_bytes = f.read()
    
    fileName = "resume.pdf"
    job_text = """
        What you'll Do
        Collaborate with a team of engineers & product managers in building a high-performance segmentation engine. Own responsibility for design and implementation of key components
        Develop query compilation algorithms that transform and rewrite segment definition queries
        Develop query optimization and evaluation algorithms including multi-query optimization, incremental evaluation and streaming evaluation
        Work on cross functional themes involving advanced data pipelines using Apache Spark
        Build tools to monitor query performance and identify & debug potential semantic errors
        Deploy production services and iteratively improve them based on customer feedback
        Follow Agile methodologies using industry leading CI/CD pipelines
        Participate in architecture, design & code reviews
        What you need to succeed
        B.S. in Computer Science or a related field is required
        M.S. in Computer Science or a related field or equivalent practical experience is preferred
        Experience building a scalable query engine or equivalent practical experience is required. Experience in language design is a plus
        Strong grasp of algorithms and data structures
        Proficiency in Databases or compilers is preferred
        Strong programming skills with extensive experience in Java or Scala
        Proficiency in Apache Spark is preferred.
        Leadership skills to collaborate and drive cross-team efforts
        Excellent communication skills
        Adaptable to evolving priorities, accepting challenges outside one's comfort zone, learning new technologies, and delivering viable solutions within defined time boundaries.
        Our compensation reflects the cost of labor across several U.S. geographic markets, and we pay differently based on those defined markets. The U.S. pay range for this position is $113,400 -- $206,300 annually. Pay within this range varies by work location and may also depend on job-related knowledge, skills, and experience. Your recruiter can share more about the specific salary range for the job location during the hiring process.
        At Adobe, for sales roles starting salaries are expressed as total target compensation (TTC = base + commission), and short-term incentives are in the form of sales commission plans.  Non-sales roles starting salaries are expressed as base salary and short-term incentives are in the form of the Annual Incentive Plan (AIP).
        In addition, certain roles may be eligible for long-term incentives in the form of a new hire equity award.
        """
    
    final_state = OrchestratorService.process_resume_and_job(
        file_bytes=pdf_bytes,
        filename=fileName,
        job_text=job_text
    )

    assert isinstance(final_state, dict)
    assert "structured_resume_doc" in final_state
    assert "job_description_doc" in final_state
    assert "tailored_resume" in final_state

    structured_resume = final_state["structured_resume_doc"]
    assert hasattr(structured_resume, "sections")
    assert len(structured_resume.sections) > 0