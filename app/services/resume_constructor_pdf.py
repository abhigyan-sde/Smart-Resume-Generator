from typing import Dict, Any
from app.models.resume_models import ResumeDocument, ResumeEntry
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import io

class ResumePDFGenerator:

    @staticmethod
    def generate_pdf(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a ResumeDocument into a PDF using its metadata and entries.
        Updates the state with 'pdf_bytes'.
        """
        print("begin pdf generator")
        resume: ResumeDocument = state.get("resume_tailored_doc")
        if not resume:
            raise ValueError("No refactored_resume found in state")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=LETTER)
        width, height = LETTER
        y_position = height - 50

        inter_section = resume.metadata.inter_section_spaces or 20
        inter_entry = resume.metadata.inter_entry_spaces or 15

        # Simple alignment helper
        def get_x_offset(alignment: str, content_width: int = 0):
            if alignment == "middle":
                return (width - content_width) / 2
            elif alignment == "right":
                return width - 50 - content_width
            return 50  # default left

        for section in sorted(resume.sections, key=lambda s: s.order):
            # Draw section header
            header: ResumeEntry = section.header
            font_name = header.font if header.font else "Helvetica-Bold"
            font_size = int(header.font_size) if header.font_size else 12
            c.setFont(font_name, font_size)
            if header.font_color:
                # Convert hex or named color to RGB, simple fallback to black
                try:
                    from reportlab.lib.colors import HexColor
                    c.setFillColor(HexColor(header.font_color))
                except:
                    pass
            x_offset = get_x_offset(resume.metadata.alignment or "left")
            c.drawString(x_offset, y_position, header.content)
            y_position -= inter_section

            # Draw entries
            for entry in section.entries:
                font_name = entry.font if entry.font else "Helvetica"
                if entry.bold:
                    font_name += "-Bold"
                if entry.italic:
                    font_name += "-Oblique"

                font_size = int(entry.font_size) if entry.font_size else 10
                c.setFont(font_name, font_size)

                if entry.font_color:
                    try:
                        from reportlab.lib.colors import HexColor
                        c.setFillColor(HexColor(entry.font_color))
                    except:
                        pass

                text_content = f"{entry.bullet_symbol or '•'} {entry.content}" if entry.bullet else entry.content
                c.drawString(x_offset + 10, y_position, text_content)
                y_position -= inter_entry

                # Check for page break
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50

        c.save()
        buffer.seek(0)
        print("end pdf generator")
        state["pdf_bytes"] = buffer.getvalue()
        return state
