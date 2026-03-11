from pydantic import BaseModel
from typing import List


class PhysicalSegment(BaseModel):
    page: int
    y: float
    xStart: float
    xEnd: float
    rawText: str

class LineModification(BaseModel):
    lineId : int
    newText: str
    segments: List[PhysicalSegment]

class ResumeGenerationPayLoad(BaseModel):
    modifications: List[LineModification]