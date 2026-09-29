import os
import google.generativeai as genai
from dotenv import load_dotenv

from config import GEMINI_MODEL_NAME

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiDocumentGenerator:
    """
    Wraps Gemini 1.5 Pro to draft structured legal documents from user-supplied
    document type, parties, terms, and effective date.
    """

    def __init__(self, model_name: str = GEMINI_MODEL_NAME):
        self.model = genai.GenerativeModel(model_name)

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        prompt = (
            f"Generate a comprehensive legal document titled '{document_type}'\n"
            f"Involved parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and conditions: {terms}\n"
            f"Ensure formal legal structure with multiple sections and legal clauses."
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating document: {e}"
