from __future__ import annotations

import re
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
CLEANED_DIR = Path("data/cleaned")

CLEANED_DIR.mkdir(parents=True, exist_ok=True)


def normalize_line_endings(text: str) -> str:
    """
    Normaliza saltos de línea en el texto.

    Convierte diferentes formatos de salto de línea (Windows, Unix, OCR)
    en un único formato estándar '\n'.

    Esto evita problemas posteriores en el pipeline cuando se realizan
    operaciones basadas en líneas como:
    - eliminación de footers
    - eliminación de ruido
    - segmentación de texto

    Parameters
    ----------
    text : str
        Texto crudo extraído del PDF.

    Returns
    -------
    str
        Texto con saltos de línea normalizados.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


def replace_ocr_artifacts(text: str) -> str:
    """
    Corrige errores comunes introducidos por OCR.

    Los documentos escaneados suelen introducir artefactos como:
    - caracteres rotos
    - ligaduras incorrectas
    - acentos corruptos
    - guiones mal interpretados

    Esta función aplica sustituciones simples para mejorar la
    legibilidad del texto antes de continuar con el pipeline.

    Examples
    --------
    conviccidn -> convicción
    afios -> años

    Parameters
    ----------
    text : str
        Texto posiblemente afectado por errores OCR.

    Returns
    -------
    str
        Texto con algunos artefactos OCR corregidos.
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
    Elimina URLs del texto.

    Los programas de gobierno suelen incluir:
    - sitios web de campaña
    - links institucionales
    - referencias externas

    Estos elementos no aportan contenido semántico relevante para
    análisis de políticas públicas y pueden interferir con
    modelos de NLP.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin URLs.
    """
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def remove_domains(text: str) -> str:
    """
    Elimina dominios web que puedan quedar después de remover URLs.

    El OCR o el parsing de PDF a veces separa partes de una URL,
    dejando fragmentos como:

    claudia-lopez.com
    gobierno.gov.co

    Esta función elimina esos restos para evitar ruido textual.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin dominios web.
    """
    return re.sub(
        r"\b[\w\.-]+\.(com|co|org|net|gov)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )


def remove_social_handles(text: str) -> str:
    """
    Elimina identificadores de redes sociales.

    Los programas de campaña frecuentemente incluyen:
    - handles de Twitter
    - cuentas de Instagram
    - redes sociales oficiales

    Estos elementos no contienen contenido programático
    relevante para análisis político.

    Examples
    --------
    @aclaudialopez
    @petrogustavo

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin handles de redes sociales.
    """
    return re.sub(r"@[A-Za-z0-9_]+", "", text)


def remove_phone_numbers(text: str) -> str:
    """
    Elimina números telefónicos.

    Los documentos de campaña a veces incluyen:
    - teléfonos de contacto
    - líneas de campaña
    - números institucionales

    Estos datos no aportan valor al análisis de políticas
    públicas y se eliminan para reducir ruido.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin números telefónicos.
    """
    return re.sub(r"\b(?:\+?\d[\d\s\-\(\)]{7,}\d)\b", "", text)


def collapse_spaces(text: str) -> str:
    """
    Reduce múltiples espacios consecutivos a un único espacio.

    El texto extraído de PDFs o OCR suele contener:
    - espacios duplicados
    - tabulaciones
    - separación irregular entre palabras

    Esta función normaliza esos casos para facilitar
    procesamiento posterior.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto con espacios normalizados.
    """
    lines = []
    for line in text.split("\n"):
        clean_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(clean_line)
    return "\n".join(lines)


def remove_campaign_footer_lines(text: str) -> str:
    """
    Elimina líneas que parecen footers de campaña.

    Muchos PDFs incluyen en cada página:
    - sitios web
    - handles de redes
    - slogans
    - branding de campaña

    Como estos elementos se repiten constantemente en el
    documento, se eliminan para evitar sesgos en análisis
    estadísticos de texto.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin líneas de footer de campaña.
    """
    cleaned_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        lower = stripped.lower()

        if not stripped:
            cleaned_lines.append("")
            continue

        if (
            ".com" in lower
            or ".co" in lower
            or "aclaudialopez" in lower
            or "claudia-lopez" in lower
            or "presidenta" in lower
            or "laudi" in lower
        ):
            continue

        if "claudialopez" in lower:
            continue

        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def remove_branding_lines(text: str) -> str:
    """
    Elimina líneas de branding político.

    Los documentos de campaña frecuentemente incluyen
    elementos visuales o de branding como:

    - slogans
    - nombres de campaña
    - palabras destacadas

    Estas líneas suelen aparecer aisladas y no contienen
    contenido programático relevante.

    Examples
    --------
    GOBIERNO
    SOLUCIONES
    COLOMBIA JUSTA

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin líneas de branding.
    """
    banned_keywords = [
        "GOBIERNO",
        "SOLUCIONES",
        "JUSTA",
        "PRESIDENTA",
        "LAUDI",
        "PORUNA",
    ]

    cleaned_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        upper = stripped.upper()

        if not stripped:
            cleaned_lines.append("")
            continue

        # eliminar líneas que contienen branding
        if any(keyword in upper for keyword in banned_keywords):
            continue

        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def remove_symbol_noise_lines(text: str) -> str:
    """
    Elimina líneas dominadas por símbolos o ruido OCR.

    Durante la extracción de texto desde PDFs escaneados,
    es común obtener líneas como:

    =) ' wGOBIERNO
    . p-E SOLUCIONES

    Estas líneas contienen pocos caracteres alfabéticos
    y muchos símbolos, por lo que se consideran ruido.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin líneas dominadas por símbolos.
    """
    cleaned_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        letters = sum(c.isalpha() for c in stripped)
        symbols = sum(not c.isalnum() and not c.isspace() for c in stripped)

        if letters <= 5 and symbols >= 2:
            continue

        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def remove_noisy_short_lines(text: str) -> str:
    """
    Elimina líneas extremadamente cortas que no contienen
    contenido semántico relevante.

    Ejemplos típicos:
    - fragmentos OCR
    - encabezados rotos
    - restos de diagramación

    La función aplica heurísticas simples para detectar
    este tipo de líneas.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto sin líneas cortas irrelevantes.
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
    Reduce múltiples líneas en blanco consecutivas.

    Los documentos extraídos de PDF suelen contener
    muchos saltos de línea vacíos generados por
    maquetación del documento.

    Esta función los reduce a una sola línea vacía.

    Parameters
    ----------
    text : str
        Texto de entrada.

    Returns
    -------
    str
        Texto con líneas en blanco normalizadas.
    """
    return re.sub(r"\n{3,}", "\n\n", text)


def clean_text(text: str) -> str:
    """
    Ejecuta el pipeline completo de limpieza textual.

    Esta función coordina todas las etapas de limpieza
    necesarias para preparar el texto para análisis NLP.

    Etapas principales:
    1. normalización de saltos de línea
    2. corrección de artefactos OCR
    3. eliminación de URLs y dominios
    4. eliminación de handles y teléfonos
    5. normalización de espacios
    6. eliminación de branding político
    7. eliminación de ruido simbólico
    8. normalización de líneas vacías

    Parameters
    ----------
    text : str
        Texto crudo proveniente del proceso de ingestión.

    Returns
    -------
    str
        Texto limpio listo para análisis posterior.
    """
    text = normalize_line_endings(text)

    text = replace_ocr_artifacts(text)

    text = remove_urls(text)
    text = remove_domains(text)
    text = remove_social_handles(text)
    text = remove_phone_numbers(text)

    text = collapse_spaces(text)

    text = remove_campaign_footer_lines(text)
    text = remove_branding_lines(text)
    text = remove_symbol_noise_lines(text)
    text = remove_noisy_short_lines(text)

    text = remove_repeated_blank_lines(text)

    return text.strip() + "\n"


def run() -> None:
    """
    Ejecuta el pipeline de limpieza para todos los textos procesados.

    Flujo del proceso:
    1. Busca archivos .txt en data/processed
    2. Lee cada documento
    3. Aplica el pipeline de limpieza
    4. Guarda el resultado en data/cleaned

    Cada documento genera un archivo:

    data/processed/
        programa_gobierno_x.txt

    →

    data/cleaned/
        programa_gobierno_x.clean.txt

    Este paso prepara los documentos para las siguientes
    etapas del proyecto, como:
    - segmentación de políticas
    - extracción de temas
    - análisis comparativo entre programas.
    """
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
