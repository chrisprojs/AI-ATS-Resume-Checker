from typing import List, Optional

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class ExperienceSummary(BaseModel):
    role: Optional[str] = Field(default=None, description="Most recent role or headline")
    years: Optional[float] = Field(default=None, description="Estimated years of experience")
    highlights: List[str] = Field(default_factory=list, description="Key bullets describing experience")

class ResumeSummary(BaseModel):
    name: Optional[str] = Field(default=None, description="Candidate name if detected")
    location: Optional[str] = Field(default=None, description="Candidate location if detected")
    work_experience: ExperienceSummary = Field(
        default_factory=ExperienceSummary,
        description="Summarized work experience details",
    )
    skills: List[str] = Field(default_factory=list, description="Key bullets for listing skills")
    score: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=10.0, 
        description="A score from 0.0 to 10.0 indicating fit for the target role"
    )
    feedbacks: List[str] = Field(default_factory=list, description="Feedbacks from cv")

class ResumeCheckerRequest:
    def __init__(
        self,
        resume_file: UploadFile = File(...),
        job_post: Optional[str] = Form(None),
    ):
        self.resume_file = resume_file
        self.job_post = job_post

class ResumeCheckerResponse(BaseModel):
    summary: ResumeSummary

