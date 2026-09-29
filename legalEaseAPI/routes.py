from fastapi import APIRouter
from pydantic import BaseModel

from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
gemini_generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    dates: str


@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    response = gemini_generator.generate_document(
        request.document_type,
        request.parties,
        request.terms,
        request.dates,
    )
    return {"document": response}
