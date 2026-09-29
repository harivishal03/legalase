import os
import re
from datetime import datetime

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

from config import LOGO_PATH, FOOTER_TEXT, COMPANY_NAME


# ---------------------------------------------------------------------------
# sanitize_text(text)
# ---------------------------------------------------------------------------
def sanitize_text(text: str) -> str:
    """
    Removes special/typographic characters (smart quotes, em-dashes, etc.)
    so downstream renderers (docx, fpdf, html) get clean, predictable text.
    """
    if not text:
        return ""

    replacements = {
        "\u2018": "'", "\u2019": "'",   # single smart quotes
        "\u201c": '"', "\u201d": '"',   # double smart quotes
        "\u2013": "-", "\u2014": "-",   # en/em dash
        "\u2026": "...",                # ellipsis
        "\u00a0": " ",                   # non-breaking space
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Strip any remaining non-printable / control characters
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", "", text)
    return text.strip()


def _split_sections(text: str):
    """Split generated text into (heading, body) blocks on markdown-style headings."""
    lines = text.split("\n")
    sections = []
    current_heading = None
    current_body = []

    heading_pattern = re.compile(r"^(#{1,3}\s+.+|^\d+\.\s+[A-Z].{0,60}:?$)")

    for line in lines:
        if heading_pattern.match(line.strip()):
            if current_heading or current_body:
                sections.append((current_heading, "\n".join(current_body).strip()))
            current_heading = line.strip().lstrip("#").strip()
            current_body = []
        else:
            current_body.append(line)

    sections.append((current_heading, "\n".join(current_body).strip()))
    return sections


def _extract_terms(terms: str):
    """Splits a semicolon-separated terms string into a clean bullet list."""
    if not terms:
        return []
    return [t.strip() for t in terms.split(";") if t.strip()]


# ---------------------------------------------------------------------------
# format_docx(text, doc_type)
# ---------------------------------------------------------------------------
def format_docx(text: str, doc_type: str, terms: str = "") -> bytes:
    """
    Builds a formatted Word document: logo header, Times New Roman body text,
    an auto-generated terms table (from semicolon-separated terms), and a footer.
    Returns the raw .docx bytes.
    """
    text = sanitize_text(text)
    document = Document()

    # Base font
    style = document.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    # Logo header
    if os.path.exists(LOGO_PATH):
        header_paragraph = document.add_paragraph()
        header_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = header_paragraph.add_run()
        run.add_picture(LOGO_PATH, width=Inches(1.3))

    # Title
    title = document.add_heading(doc_type, level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Body content, split into headed sections
    for heading, body in _split_sections(text):
        if heading:
            document.add_heading(heading, level=2)
        if body:
            for para in body.split("\n"):
                if para.strip():
                    document.add_paragraph(para.strip())

    # Terms table (if terms were supplied separately)
    term_items = _extract_terms(terms)
    if term_items:
        document.add_heading("Terms & Conditions", level=2)
        table = document.add_table(rows=1, cols=1)
        table.style = "Light Grid Accent 1"
        table.rows[0].cells[0].text = "Term"
        for term in term_items:
            row_cells = table.add_row().cells
            row_cells[0].text = term

    # Footer
    section = document.sections[0]
    footer = section.footer
    footer_paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_paragraph.text = FOOTER_TEXT
    footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    from io import BytesIO
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# format_pdf(text, doc_type)
# ---------------------------------------------------------------------------
class _LegalPDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            # Center the logo
            logo_width = 25
            x = (self.w - logo_width) / 2
            self.image(LOGO_PATH, x=x, y=8, w=logo_width)
            self.set_y(8 + 20)
        self.set_font("Times", "B", 16)
        self.cell(0, 10, self.title_text, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 8)
        self.cell(0, 10, FOOTER_TEXT, align="C")


def format_pdf(text: str, doc_type: str, terms: str = "") -> bytes:
    """
    Builds a branded PDF: centered logo + title header on every page, bold
    section headings, bullet-style terms, and a footer with company info.
    Returns the raw .pdf bytes.
    """
    text = sanitize_text(text)

    pdf = _LegalPDF()
    pdf.title_text = doc_type
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Times", "", 12)

    for heading, body in _split_sections(text):
        if heading:
            pdf.set_font("Times", "B", 13)
            pdf.multi_cell(0, 8, heading)
            pdf.ln(1)
            pdf.set_font("Times", "", 12)
        if body:
            for para in body.split("\n"):
                if para.strip():
                    pdf.multi_cell(0, 7, para.strip())
                    pdf.ln(1)

    term_items = _extract_terms(terms)
    if term_items:
        pdf.set_font("Times", "B", 13)
        pdf.multi_cell(0, 8, "Terms & Conditions")
        pdf.set_font("Times", "", 12)
        for term in term_items:
            pdf.multi_cell(0, 7, f"- {term}")

    output = pdf.output(dest="S")
    if isinstance(output, str):
        output = output.encode("latin-1", "replace")
    return bytes(output)


# ---------------------------------------------------------------------------
# format_html_preview(text)
# ---------------------------------------------------------------------------
def format_html_preview(text: str) -> str:
    """
    Converts the generated document text into stylized HTML for the
    dark-themed, scrollable Streamlit preview card.
    """
    text = sanitize_text(text)
    html_parts = []

    for heading, body in _split_sections(text):
        if heading:
            html_parts.append(f"<h3 style='color:#e8e8f0;margin-top:18px;'>{heading}</h3>")
        for para in body.split("\n"):
            if para.strip():
                html_parts.append(
                    f"<p style='color:#c9c9d6;line-height:1.6;margin:6px 0;'>{para.strip()}</p>"
                )

    return "\n".join(html_parts)
