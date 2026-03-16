from __future__ import annotations

import re
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
CLEANED_DIR = Path("data/cleaned")

CLEANED_DIR.mkdir(parents=True, exist_ok=True)


def normalize_line_endings(text: str) -> str:
    """
    Unifica saltos de línea.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


def replace_ocr_artifacts(text: str) -> str:
    """
    Limpia algunos artefactos comunes de OCR.
    """
    replacements = {
        "\u00a0": " ",  # non-breaking space
        "\ufeff": "",  # BOM
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "—": "-",
        "–": "-",
        "…": "...",
        "|": " ",
        "©": " ",
        "®": " ",
        "™": " ",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


def remove_urls(text: str) -> str:
    """
    Elimina URLs completas.
    """
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def remove_domains(text: str) -> str:
    """
    Elimina dominios web como .com, .co, .org, etc.
    """
    return re.sub(r"\b\S+\.(com|co|org|net|gov)\b", "", text)


def remove_social_handles(text: str) -> str:
    """
    Elimina handles tipo @usuario.
    """
    return re.sub(r"(?<!\w)@[A-Za-z0-9_\.]+", "", text)


def remove_phone_numbers(text: str) -> str:
    """
    Elimina números telefónicos simples.
    """
    return re.sub(r"\b(?:\+?\d[\d\s\-\(\)]{7,}\d)\b", "", text)


def collapse_spaces(text: str) -> str:
    """
    Reduce múltiples espacios y tabs a un solo espacio,
    preservando saltos de línea.
    """
    lines = []
    for line in text.split("\n"):
        clean_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(clean_line)
    return "\n".join(lines)


def remove_symbol_noise_lines(text: str) -> str:
    """
    Elimina líneas con demasiados símbolos y pocas letras.
    Útil para portadas OCR rotas.
    """
    cleaned_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        letters = sum(c.isalpha() for c in stripped)
        symbols = sum(not c.isalnum() and not c.isspace() for c in stripped)

        # si tiene pocos caracteres alfabéticos y muchos símbolos → ruido
        if letters < 3 and symbols > 2:
            continue

        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def remove_noisy_short_lines(text: str) -> str:
    """
    Elimina líneas muy cortas y ruidosas, pero conserva números
    romanos y títulos cortos razonables.
    """
    cleaned_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        # eliminar líneas de solo símbolos
        if re.fullmatch(r"[\W_]+", stripped):
            continue

        # eliminar líneas ultra cortas de puro ruido OCR
        if len(stripped) <= 2 and not re.fullmatch(r"[IVXLCDM0-9]+", stripped):
            continue

        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def remove_repeated_blank_lines(text: str) -> str:
    """
    Deja como máximo una línea en blanco entre bloques.
    """
    return re.sub(r"\n{3,}", "\n\n", text)


def clean_text(text: str) -> str:
    """
    Pipeline básico de limpieza.
    """
    text = normalize_line_endings(text)
    text = replace_ocr_artifacts(text)
    text = remove_urls(text)
    text = remove_social_handles(text)
    text = remove_phone_numbers(text)
    text = collapse_spaces(text)
    text = remove_noisy_short_lines(text)
    text = remove_repeated_blank_lines(text)

    return text.strip() + "\n"


def run() -> None:
    print("\n[PIPELINE] TEXT CLEANING START\n")

    txt_files = sorted(PROCESSED_DIR.glob("*.txt"))

    if not txt_files:
        print("[WARN] No .txt files found in data/processed")
        return

    for txt_path in txt_files:
        print(f"[INFO] Cleaning: {txt_path.name}")

        raw_text = txt_path.read_text(encoding="utf-8", errors="ignore")

        cleaned_text = clean_text(raw_text)

        output_path = CLEANED_DIR / f"{txt_path.stem}.clean.txt"

        output_path.write_text(cleaned_text, encoding="utf-8")

        print(f"[OK] Saved: {output_path.name}")
        print("\n[PIPELINE] TEXT CLEANING COMPLETE\n")


if __name__ == "__main__":
    run()
