from typing import List, Optional

from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExperienceEntry(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class SuggestedRole(BaseModel):
    title: str
    reason: str


class ParseResponse(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    links: List[str] = Field(default_factory=list)

    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)

    resume_score: int = Field(ge=0, le=100)
    score_breakdown: Optional[str] = None
    suggested_roles: List[SuggestedRole] = Field(default_factory=list)

    original_filename: str


class ErrorResponse(BaseModel):
    detail: str
