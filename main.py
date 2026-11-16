import io
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from sqlalchemy.orm import Session

try:
    from . import models, schemas
    from .ai import extract_structured, ExtractionError, PROFILE_INSTRUCTIONS, JD_INSTRUCTIONS
    from .database import Base, engine, get_db
except ImportError:
    import models, schemas
    from ai import extract_structured, ExtractionError, PROFILE_INSTRUCTIONS, JD_INSTRUCTIONS
    from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)
app = FastAPI(title="TalentVerse")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def read_upload(file: UploadFile | None, text: str | None) -> str:
    if file is not None:
        data = file.file.read()
        if file.filename.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(data))
            content = "\n".join(p.extract_text() or "" for p in reader.pages)
        else:
            content = data.decode("utf-8", errors="ignore")
    else:
        content = text or ""
    if len(content.strip()) < 50:
        raise HTTPException(400, "Could not read enough text from the input.")
    return content


@app.get("/health")
def health():
    return {"status": "ok"}


# Step 1: AI extracts and validates a DRAFT. Nothing is saved yet.
@app.post("/profiles/extract", response_model=schemas.CandidateProfile)
def extract_profile(file: UploadFile | None = File(None), text: str | None = Form(None)):
    content = read_upload(file, text)
    try:
        return extract_structured(content, schemas.CandidateProfile, PROFILE_INSTRUCTIONS)
    except ExtractionError as e:
        raise HTTPException(422, str(e))


# Step 2: user reviews/edits the draft in the UI, then it is re-validated and saved.
@app.post("/profiles")
def save_profile(profile: schemas.CandidateProfile, db: Session = Depends(get_db)):
    row = models.Profile(name=profile.name, email=profile.email, raw_json=profile.model_dump_json())
    row.skills = [models.Skill(**s.model_dump()) for s in profile.skills]
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id}


@app.get("/profiles/{profile_id}")
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Profile, profile_id)
    if not row:
        raise HTTPException(404, "Profile not found")
    return {
        "id": row.id,
        "name": row.name,
        "email": row.email,
        "skills": [{"id": s.id, "name": s.name, "level": s.level, "evidence": s.evidence} for s in row.skills],
    }


@app.post("/jobs/extract", response_model=schemas.JobRequirements)
def extract_job(text: str = Form(...)):
    if len(text.strip()) < 50:
        raise HTTPException(400, "Job description is too short.")
    try:
        return extract_structured(text, schemas.JobRequirements, JD_INSTRUCTIONS)
    except ExtractionError as e:
        raise HTTPException(422, str(e))


@app.post("/jobs")
def save_job(job: schemas.JobRequirements, db: Session = Depends(get_db)):
    row = models.JobDescription(title=job.title, company=job.company, raw_json=job.model_dump_json())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id}
