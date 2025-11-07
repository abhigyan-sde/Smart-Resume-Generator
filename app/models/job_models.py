from pydantic import BaseModel
from typing import Optional, Dict, Set

class JobDescriptionDocument(BaseModel):
    title: Optional[str]
    company: Optional[str]
    location: Optional[str]

    # Core tailoring inputs
    responsibilities: Set[str]                # “What you'll do”
    qualifications: Set[str]                  # Education + generic reqs (verbatim lines)
    technical_skills: Set[str]                # Raw extracted skills/tools

    # Small but powerful additions
    role: Optional[str] = None                 # e.g., "Software Engineer"
    seniority: Optional[str] = None            # e.g., "Mid", "Senior"
    domain: Set[str] = []                     # e.g., ["Backend", "Platform"]

    must_have_skills: Set[str] = []           # subset of technical_skills
    nice_to_have_skills: Set[str] = []        # subset of technical_skills

    years_experience_min: Optional[float] = None
    years_experience_pref: Optional[float] = None
    education_required: Optional[str] = None   # e.g., "BS in CS or related"

    # Normalization aids for better matching
    normalized_skills: Dict[str, Set[str]] = {}  # {"javascript": ["JS","JavaScript","ECMAScript"]}
    priority_weights: Dict[str, float] = {}       # {"kubernetes": 1.5, "python": 1.2}

    source_url: Optional[str] = None
    raw_text: Optional[str] = None


class JobParseRequest(BaseModel):
    url: Optional[str] = None
    job_text: Optional[str] = None