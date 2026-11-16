"""Pydantic models = the contract between the LLM and the database.
Every AI output must validate against one of these before it is saved."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

Level = Literal["beginner", "intermediate", "advanced"]


class Skill(BaseModel):
    name: str = Field(min_length=1)
    level: Level
    evidence: str = Field(description="Short phrase from the resume that supports this skill")


class Education(BaseModel):
    institution: str
    degree: str
    year: Optional[str] = None


class Experience(BaseModel):
    role: str
    org: str
    duration: Optional[str] = None
    highlights: list[str] = []


class Project(BaseModel):
    title: str
    tech: list[str] = []
    summary: str = ""


class CandidateProfile(BaseModel):
    name: str
    email: Optional[str] = None
    skills: list[Skill] = Field(min_length=1)
    education: list[Education] = []
    experience: list[Experience] = []
    projects: list[Project] = []


class RequiredSkill(BaseModel):
    name: str
    importance: int = Field(ge=1, le=5, description="5 = critical for the role")
    must_have: bool


class JobRequirements(BaseModel):
    title: str
    company: Optional[str] = None
    required_skills: list[RequiredSkill] = Field(min_length=1)
    responsibilities: list[str] = []


# Used in the next step (gap analysis + learning plan)
class GapItem(BaseModel):
    skill: str
    importance: int = Field(ge=1, le=5)
    status: Literal["have", "partial", "missing"]
    note: str = ""


class GapAnalysis(BaseModel):
    match_score: int = Field(ge=0, le=100)
    gaps: list[GapItem]


class MilestoneIn(BaseModel):
    title: str
    skill: str
    description: str
    week: int = Field(ge=1)


class LearningPlan(BaseModel):
    milestones: list[MilestoneIn] = Field(min_length=1)
