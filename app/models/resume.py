from typing import List, Optional, Set, Dict
from pydantic import BaseModel, Field
import uuid


class BBox(BaseModel):
    """Bounding box of text on a page (PDF coords)."""
    x0: float
    top: float
    x1: float
    bottom: float


class RunMeta(BaseModel):
    """Metadata for a character run (from DOCX or PDF)."""
    text: str
    font: Optional[str] = None
    font_size: Optional[float] = None
    bold: Optional[bool] = False
    italic: Optional[bool] = False
    font_color: Optional[str] = None


class ResumeEntry(BaseModel):
    """Represents a minimal unit of content (line, bullet, or paragraph)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    runs: Optional[List[RunMeta]] = []

    # Presentation metadata
    font: Optional[str] = None
    font_size: Optional[float] = None
    font_color: Optional[str] = None
    bold: bool = False
    italic: bool = False
    bullet: bool = False
    bullet_symbol: Optional[str] = None
    technical_skills: Set[str] = set()

    # Positional / layout metadata
    page: int = 1
    bbox: Optional[BBox] = None
    column: Optional[int] = None
    x_center: Optional[float] = None
    y_center: Optional[float] = None
    line_index: Optional[int] = None
    paragraph_index: Optional[int] = None

    # Structural relationships
    group_id: Optional[str] = None          # group multiple entries (e.g., one job)
    parent_id: Optional[str] = None         # reference a header/section entry
    is_header: bool = False
    block_type: Optional[str] = None        # "header", "paragraph", "bullet", etc.


class ResumeSection(BaseModel):
    """Logical section in the resume (Work Experience, Projects, Summary, etc.)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str                                 # "Work Experience", "Projects", etc.
    header: Optional[ResumeEntry] = None      # The section header itself
    entries: List[ResumeEntry] = []
    order: Optional[int] = None               # Order in the document
    page_start: Optional[int] = None
    page_end: Optional[int] = None


class ResumeMetadata(BaseModel):
    """Summary layout & formatting info for the whole resume."""
    border: bool = False
    pages: int = 1
    columns_by_page: Dict[int, int] = {}      # e.g., {1: 2, 2: 1}
    entry_per_column: Optional[int] = None
    alignment: Optional[str] = "left"         # left, center, right
    inter_section_spaces: Optional[float] = None
    inter_entry_spaces: Optional[float] = None
    avg_font_size: Optional[float] = None
    page_widths: Optional[Dict[int, float]] = None


class ResumeDocument(BaseModel):
    """Top-level container for a parsed resume."""
    sections: List[ResumeSection]
    metadata: ResumeMetadata
    source: Optional[str] = None

    # Optional denormalized cache (flat list of all entries for easy global ops)
    entries: Optional[List[ResumeEntry]] = None

    def build_flat_entries(self):
        """Helper to flatten sections into entries (for search/LLM)."""
        self.entries = [entry for sec in self.sections for entry in sec.entries]

