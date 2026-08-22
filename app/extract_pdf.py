"""Pull selectable text from a PDF on this machine. No OCR, no cloud."""

from __future__ import annotations

from io import BytesIO

MAX_PDF_BYTES = 2 * 1024 * 1024
MAX_TEXT_CHARS = 200 * 1024


def extract_pdf_text(raw: bytes) -> tuple[str, int]:
    if not raw:
        raise ValueError("That PDF is empty.")
    if len(raw) > MAX_PDF_BYTES:
        raise ValueError("That PDF is over 2 MB. Use a smaller file, or paste the text.")
    if not raw.lstrip().startswith(b"%PDF"):
        raise ValueError("That file is not a PDF.")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF reading is not installed on this machine.") from exc
    try:
        reader = PdfReader(BytesIO(raw))
    except Exception as exc:
        raise ValueError("Could not read that PDF.") from exc
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n\n".join(part.strip() for part in pages if part and part.strip()).strip()
    if not text:
        raise ValueError("No selectable text in that PDF. Paste the text instead.")
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]
    return text, len(reader.pages)
