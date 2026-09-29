# LegalEase — AI-Powered Legal Document Generator

Generates structured legal documents (contracts, NDAs, lease agreements, etc.)
from user-supplied document type, parties, terms, and effective date, using
Google's Gemini 1.5 Pro. Backend is FastAPI; frontend is Streamlit; documents
can be exported as .TXT, .DOCX, or .PDF with logo + footer branding.

## Setup

    python -m venv venv
    source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r requirements.txt

Copy `.env.example` to `.env` and add your Gemini API key:

    cp .env.example .env

Replace the placeholder images in `Image/Logo.png` and
`Image/inverseLogo.png` with your own branding if you like.

## Run

Option A — one command (starts both backend and frontend):

    ./run.sh

Option B — run each manually, in two terminals:

    uvicorn legalEaseAPI.main:app --reload --port 8000
    streamlit run frontend/app.py

Then visit:
- http://localhost:8501       (Streamlit UI)
- http://localhost:8000/docs  (FastAPI interactive API docs)

## Structure

    legalease/
    ├── requirements.txt
    ├── .env.example
    ├── config.py                      # shared paths & constants
    ├── run.sh                         # launches backend + frontend together
    ├── ai_core/
    │   ├── gemini_generator.py        # GeminiDocumentGenerator (Gemini 1.5 Pro)
    │   └── generator.py               # sanitize_text, format_docx, format_pdf,
    │                                  # format_html_preview
    ├── legalEaseAPI/
    │   ├── main.py                     # FastAPI app entry point
    │   └── routes.py                   # DocumentRequest model + /generate route
    ├── frontend/
    │   └── app.py                      # Streamlit UI
    ├── Image/
    │   ├── Logo.png                    # used in DOCX/PDF branding
    │   └── inverseLogo.png             # used on the dark Streamlit UI
    └── docs/                           # (place any reference docs here)

## Notes

- The `terms` field uses semicolons to separate individual clauses
  (e.g. `Payment due in 30 days; Confidentiality applies; 15-day termination notice`).
  These are rendered as a table in the .DOCX export and as bullet points in the .PDF export.
- `BACKEND_URL` (default `http://localhost:8000`) can be overridden via an
  environment variable if you deploy the backend separately from the frontend.
