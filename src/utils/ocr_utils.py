from pathlib import Path
from typing import Any

import fitz
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_with_ocr(pdf_path: Path) -> tuple[str, dict[str, Any]]:
    doc = fitz.open(pdf_path)

    text_parts: list[str] = []
    page_char_counts: list[int] = []
    ocr_language = "spa"

    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)

        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        try:
            page_text = pytesseract.image_to_string(img, lang="spa")
        except pytesseract.TesseractError:
            ocr_language = "default"
            page_text = pytesseract.image_to_string(img)

        page_text = page_text.strip()
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
        "extraction_method": "ocr",
        "fallback_used": True,
        "ocr_language": ocr_language,
    }

    doc.close()
    return full_text, metadata
