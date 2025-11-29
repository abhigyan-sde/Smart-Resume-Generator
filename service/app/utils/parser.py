import io
import pdfplumber
import tempfile
import os
from docx2pdf import convert


class Parser:        
    
    @staticmethod
    def extract_resume_text_from_doc(file_bytes: bytes) -> str:
        """
        Converts DOCX to PDF internally and parses it using the same pdfParser logic.
        Returns a unified ResumeDocument.
        """

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
            temp_docx.write(file_bytes)
            temp_docx_path = temp_docx.name

        temp_pdf_path = temp_docx_path.replace(".docx", ".pdf")

        try:
            # Convert DOCX → PDF
            convert(temp_docx_path, temp_pdf_path)

            # Read the generated PDF
            with open(temp_pdf_path, "rb") as f:
                pdf_bytes = f.read()

            # Parse using existing pdfParser
            return Parser.extract_resume_text_from_doc(pdf_bytes)

        except Exception as e:
            raise RuntimeError(f"Error converting DOCX to PDF: {e}")

        finally:
            # Clean up temp files
            for path in [temp_docx_path, temp_pdf_path]:
                if os.path.exists(path):
                    os.remove(path)

    @staticmethod
    def extract_resume_text_from_pdf(file_bytes: bytes) -> str:
        """Extract all text from PDF file bytes as a single string."""
        all_text = []

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text.append(page_text.strip())

        # Join all pages with newlines
        resume_text = "\n".join(all_text)
        return resume_text