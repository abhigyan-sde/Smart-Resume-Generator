from typing import List, Optional, Set, Dict
from pydantic import BaseModel, Field
import uuid

class ResumeEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # unique identifier
    content: str
    font: Optional[str] = None
    font_size: Optional[str] = None
    font_color: Optional[str] = None
    bold: bool = False
    italic: bool = False
    bullet: bool = False
    bullet_symbol: Optional[str] = None
    technical_skills: Set[str] = set() # technical skills per entry if present


class Section(BaseModel):
    header: ResumeEntry
    order: int
    entries: List[ResumeEntry]


class ResumeMetadata(BaseModel):
    border: bool = False
    columns: int = 0
    entry_per_column: int = 0
    pages: int = 1
    alignment: Optional[str] = "left"  # left, middle, right
    inter_section_spaces: Optional[int] = None
    inter_entry_spaces: Optional[int] = None


class ResumeDocument(BaseModel):
    sections: List[Section]
    metadata: ResumeMetadata
    all_skills: Set[str] = set() # technical skills for the overall resume
    normalized_skills: Dict[str, Set[str]] = {} 