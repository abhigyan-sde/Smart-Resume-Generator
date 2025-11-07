from typing import Dict, Any
from app.utils.parser import Parser

class ResumeParser:

    @staticmethod
    def parse_resume(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node function for LangGraph.
        Converts resume bytes into structured ResumeDocument.
        """
        file_bytes = state.get("resume_file_bytes")
        filename = state.get("resume_filename")

        if not file_bytes or not filename:
            raise ValueError("resume_file_bytes and resume_filename are required in state")

        ext = filename.lower().split(".")[-1]

        if ext == "pdf":
            structured_resume = Parser.pdfParser(file_bytes)
        else:
            structured_resume = Parser.docParser_2(file_bytes)

        state["structured_resume_doc"] = structured_resume
        return state