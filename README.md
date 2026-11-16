# TalentVerse backend

    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env    # add your API key
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs to test every endpoint (no Postman needed).

Flow: POST /profiles/extract (resume) -> review -> POST /profiles (saves to DB) -> GET /profiles/{id}
