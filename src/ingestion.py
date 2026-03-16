from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pdf_text_extractor import extract_text_from_pdf
from utils.ocr_utils import extract_text_with_ocr

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_extraction(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Evalúa si la extracción textual fue suficiente o si conviene OCR.
    """
    pages = metadata.get("pages", 0) or 0
    text_chars = metadata.get("text_chars", 0) or 0
    empty_pages = metadata.get("empty_pages", 0) or 0

    if text_chars == 0:
        status = "needs_ocr"
        needs_ocr = True
    elif pages > 5 and text_chars < 500:
        status = "low_text"
        needs_ocr = True
    elif pages > 0 and empty_pages == pages:
        status = "needs_ocr"
        needs_ocr = True
    else:
        status = "ok"
        needs_ocr = False

    metadata["status"] = status
    metadata["needs_ocr"] = needs_ocr
    return metadata


def save_outputs(text: str, metadata: dict[str, Any], pdf_path: Path) -> None:
    """
    Guarda el txt y el meta.json en data/processed.
    """
    txt_output = PROCESSED_DIR / f"{pdf_path.stem}.txt"
    meta_output = PROCESSED_DIR / f"{pdf_path.stem}.meta.json"

    txt_output.write_text(text, encoding="utf-8")

    with meta_output.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def run() -> None:
    for pdf_path in RAW_DIR.rglob("*.pdf"):
        print(f"[INFO] Procesando: {pdf_path.name}")

        text, metadata = extract_text_from_pdf(pdf_path)
        metadata = evaluate_extraction(metadata)

        if metadata["needs_ocr"]:
            print(f"[WARN] {pdf_path.name}: extracción pobre, OCR sugerido")

            # fallback OCR (por ahora placeholder)
            ocr_text, ocr_metadata = extract_text_with_ocr(pdf_path)

            # solo reemplazar si OCR devolvió algo útil
            if len(ocr_text.strip()) > len(text.strip()):
                text = ocr_text
                metadata.update(ocr_metadata)
                metadata["status"] = "ok_after_ocr"
                metadata["needs_ocr"] = False

        save_outputs(text, metadata, pdf_path)
        print(f"[OK] Guardado: {pdf_path.stem}.txt y .meta.json")


if __name__ == "__main__":
    run()
