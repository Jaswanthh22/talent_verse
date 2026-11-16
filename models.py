from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
try:
    from .database import Base
except ImportError:
    from database import Base


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    raw_json: Mapped[str] = mapped_column(Text)  # full validated profile, for the report/viva
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    skills: Mapped[list["Skill"]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    name: Mapped[str] = mapped_column(String(100))
    level: Mapped[str] = mapped_column(String(20))
    evidence: Mapped[str] = mapped_column(Text)
    profile: Mapped[Profile] = relationship(back_populates="skills")


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    raw_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# Next: GapAnalysis, LearningPlan, Milestone (status, due_date) tables.
