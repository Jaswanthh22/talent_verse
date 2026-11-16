# TalentVerse

TalentVerse is an AI-assisted talent profiling backend. It extracts structured candidate profiles from resumes and job requirements from job descriptions, validates every AI response with Pydantic, and stores approved records in a relational database.

## What it does

- Extracts candidate name, contact details, skills, education, experience, and projects from resume text or PDF files.
- Extracts required skills, importance, responsibilities, and must-have requirements from job descriptions.
- Uses a review-before-save workflow: AI creates a draft, then the client submits the reviewed JSON for persistence.
- Stores profiles, skills, and job descriptions with SQLAlchemy.
- Exposes interactive API documentation through FastAPI at `/docs`.

## Architecture

```text
Resume / job description
          │
          ▼
   FastAPI extraction endpoint
          │
          ▼
   Gemini structured extraction
          │
          ▼
   Pydantic validation + retry
          │
          ▼
   Review in client → save to database
```

## Requirements

- Python 3.10+
- A Google Gemini API key for AI extraction
- SQLite for local development, or PostgreSQL for deployment

## Quick start

```bash
git clone https://github.com/Jaswanthh22/talent_verse.git
cd talent_verse

python -m venv venv
source venv/bin/activate       # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

python -m uvicorn main:app --reload
```

The API is available at <http://127.0.0.1:8000>. Open <http://127.0.0.1:8000/docs> for the interactive Swagger UI.

## Configuration

Create a `.env` file from `.env.example`:

```dotenv
DATABASE_URL=sqlite:///./talentverse.db
GEMINI_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-2.5-flash
```

Never commit `.env`, API keys, or local database files. They are excluded by `.gitignore`.

For PostgreSQL, set `DATABASE_URL` to a SQLAlchemy-compatible connection string, for example:

```dotenv
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/talentverse
```

## API workflow

### 1. Check service health

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{"status":"ok"}
```

### 2. Extract a candidate profile

From a PDF or text resume:

```bash
curl -X POST http://127.0.0.1:8000/profiles/extract \
  -F "file=@resume.pdf"
```

Or submit resume text directly:

```bash
curl -X POST http://127.0.0.1:8000/profiles/extract \
  -F "text=Jane Doe has five years of Python and FastAPI experience..."
```

The response is a validated draft. Review or edit it in the client before saving.

### 3. Save the reviewed profile

```bash
curl -X POST http://127.0.0.1:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "skills": [
      {
        "name": "Python",
        "level": "advanced",
        "evidence": "Five years building Python services"
      }
    ],
    "education": [],
    "experience": [],
    "projects": []
  }'
```

### 4. Retrieve a saved profile

```bash
curl http://127.0.0.1:8000/profiles/1
```

### 5. Extract and save job requirements

```bash
curl -X POST http://127.0.0.1:8000/jobs/extract \
  -F "text=We are hiring a backend engineer with Python, FastAPI, and PostgreSQL experience..."
```

After review, save the validated result with `POST /jobs`:

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Backend Engineer",
    "company": "Example Co",
    "required_skills": [
      {"name": "Python", "importance": 5, "must_have": true}
    ],
    "responsibilities": ["Build and maintain backend APIs"]
  }'
```

## Endpoints

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health check |
| `POST` | `/profiles/extract` | Extract a candidate profile from PDF or text |
| `POST` | `/profiles` | Validate and save a reviewed candidate profile |
| `GET` | `/profiles/{profile_id}` | Retrieve a saved profile and its skills |
| `POST` | `/jobs/extract` | Extract requirements from a job description |
| `POST` | `/jobs` | Validate and save reviewed job requirements |

## Project structure

```text
.
├── main.py          # FastAPI application and routes
├── ai.py            # Gemini client and schema-guided extraction
├── database.py      # SQLAlchemy engine and session management
├── models.py        # Database models
├── schemas.py       # Pydantic request/response contracts
├── requirements.txt
├── .env.example
└── .gitignore
```

## Validation and error handling

AI output is requested as JSON, parsed against the relevant Pydantic schema, and retried once with validation feedback if it fails. The API returns:

- `400` when an upload or job description does not contain enough text.
- `404` when a requested profile does not exist.
- `422` when the AI cannot produce schema-valid output after retrying.

## Current scope

The database models include profiles, skills, and job descriptions. Gap analysis, learning plans, and milestone tracking are represented by schema placeholders and are planned for a future iteration.

## License

No license has been specified yet.
