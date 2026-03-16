"""
extrae texto normal con PyMuPDF
"""

from pathlib import Path
from typing import Any

import fitz


def extract_text_from_pdf(pdf_path: Path) -> tuple[str, dict[str, Any]]:
    """
    Extrae texto desde un PDF textual usando PyMuPDF.
    Devuelve:
      - full_text: texto completo unido
      - metadata: información básica de extracción
    """
    doc = fitz.open(pdf_path)

    text_parts: list[str] = []
    page_char_counts: list[int] = []

    for page in doc:
        page_text = str(page.get_text("text")).strip()

        if not page_text:
            page_text = str(page.get_text()).strip()

        text_parts.append(page_text)
        page_char_counts.append(len(page_text))

    full_text = "\n".join(text_parts).strip()

    metadata = {
        "source_file": pdf_path.name,
        "pages": len(doc),
        "text_chars": len(full_text),
        "word_count": len(full_text.split()),
        "page_char_counts": page_char_counts,
        "empty_pages": sum(1 for n in page_char_counts if n == 0),
        "extraction_method": "pymupdf",
        "fallback_used": False,
    }

    doc.close()
    return full_text, metadata
