import os
import sys

# Allow running `streamlit run frontend/app.py` from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st

from config import WEB_LOGO_PATH, BACKEND_URL
from ai_core.generator import sanitize_text, format_docx, format_pdf, format_html_preview

st.set_page_config(page_title="LegalEase", layout="centered")

# --- Header: centered logo + title -----------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(WEB_LOGO_PATH):
        st.image(WEB_LOGO_PATH, use_container_width=True)

st.markdown(
    "<h2 style='text-align: center;'>AI Legal Document Generator</h2>",
    unsafe_allow_html=True,
)

# --- User input --------------------------------------------------------------
document_type = st.text_input("Document Type (Ex: Agreement, Contract, NDA)")
parties = st.text_area("Parties Involved")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)")
dates = st.text_input("Effective Date")

# --- Session state defaults --------------------------------------------------
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False

generate_clicked = st.button("Generate Document")

if generate_clicked:
    if not document_type or not parties or not terms or not dates:
        st.warning("Please fill in all fields before generating the document.")
    else:
        with st.spinner("Generating your document..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "dates": dates,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                st.session_state.generated_text = sanitize_text(response.json()["document"])
                st.success("Document Generated Successfully!")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# --- Preview / Edit / Download ------------------------------------------------
if st.session_state.generated_text:
    generated_text = st.session_state.generated_text

    styled_html = format_html_preview(generated_text)
    st.markdown(
        f"<div style='background:#12131a;border-radius:10px;padding:18px 22px;"
        f"max-height:420px;overflow-y:auto;'>{styled_html}</div>",
        unsafe_allow_html=True,
    )

    if st.button("Click to Edit Document"):
        st.session_state.show_edit = not st.session_state.show_edit

    if st.session_state.show_edit:
        edited_text = st.text_area(
            "Edit Document Below:", generated_text, height=300
        )
        st.session_state.generated_text = edited_text
        generated_text = edited_text

    file_stub = document_type.replace(" ", "_").lower() if document_type else "legal_document"

    st.download_button(
        "📄 Download as .TXT",
        data=generated_text,
        file_name=f"{file_stub}.txt",
    )
    st.download_button(
        "📝 Download as .DOCX",
        data=format_docx(generated_text, document_type or "Legal Document", terms),
        file_name=f"{file_stub}.docx",
    )
    st.download_button(
        "📕 Download as .PDF",
        data=format_pdf(generated_text, document_type or "Legal Document", terms),
        file_name=f"{file_stub}.pdf",
    )
else:
    st.info("Click 'Generate Document' to start")
