import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logo assets used in DOCX / PDF / Streamlit branding
LOGO_PATH = os.path.join(BASE_DIR, "Image", "Logo.png")
INVERSE_LOGO_PATH = os.path.join(BASE_DIR, "Image", "inverseLogo.png")
WEB_LOGO_PATH = INVERSE_LOGO_PATH  # used on the dark Streamlit UI

# Backend URL the Streamlit frontend calls
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Gemini model used across the app
GEMINI_MODEL_NAME = "gemini-3.1-pro-preview"

# Branding text used in PDF/DOCX footers
COMPANY_NAME = "LegalEase Inc."
COMPANY_CONTACT = "contact@legalease.com"
FOOTER_TEXT = f"{COMPANY_NAME} | {COMPANY_CONTACT} | All Rights Reserved."
