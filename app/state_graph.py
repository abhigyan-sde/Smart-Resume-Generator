from typing import Dict, Any
from langgraph.graph import StateGraph, END  # type: ignore

# Import node functions from your services
# Each node must accept `state: Dict[str, Any]` and return an updated dict.
from app.services.resumeParser import ResumeParser  # exposes parse_node(state)->dict
from app.services.job_parser import JobParser              # exposes parse_node(state)->dict
from app.services.resume_tailor import TailoringService        # exposes tailor_node(state)->dict
from app.services.resume_constructor_pdf import ResumePDFGenerator    # exposes render_node(state)->dict


def build_graph():
    """
    Build the LangGraph state graph for resume tailoring pipeline.

    Initial state keys (input):
      - resume_filename: str
      - resume_file_base64: str (data URI: data:<mime>;base64,<...>)
      - job_text: str
      - job_url: Optional[str]

    State keys added/updated by nodes:
      - structured_resume_doc: ResumeDocument
      - job_description_doc: JobDescriptionDocument
      - resume_tailored_doc: ResumeDocument
      - pdf_bytes: bytes
    """
    graph = StateGraph(dict)

    # Nodes
    graph.add_node("parse_resume", ResumeParser.parse_resume)
    graph.add_node("parse_job", JobParser.parse_job_posting)
    graph.add_node("tailor_resume", TailoringService.tailor_resume)
    graph.add_node("render_pdf", ResumePDFGenerator.generate_pdf)

    # Entry + edges
    graph.set_entry_point("parse_resume")
    graph.add_edge("parse_resume", "parse_job")
    graph.add_edge("parse_job", "tailor_resume")
    graph.add_edge("tailor_resume", "render_pdf")
    graph.add_edge("render_pdf", END)

    return graph.compile()


# Build a single compiled graph at import time.
APP_GRAPH = build_graph()


def run_pipeline(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke the compiled graph with the caller-provided initial state.
    No graph node should handle initialization.
    """
    return APP_GRAPH.invoke(initial_state)
