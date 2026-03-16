import csv
from pathlib import Path

from candidate_registry import CANDIDATES

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
MANIFEST_DIR = BASE_DIR / "data" / "manifests"
MANIFEST_FILE = MANIFEST_DIR / "sources.csv"

FIELDNAMES = [
    "candidate_id",
    "candidate_name",
    "bloc",
    "country",
    "election_year",
    "source_priority",
    "source_type",
    "document_level",
    "document_type",
    "access_method",
    "title",
    "url",
    "file_type",
    "local_filename",
    "is_official",
    "status",
    "notes",
    "analysis_eligibility",
]

SEED_SOURCES = [
    {
        "candidate_id": "ivan_cepeda",
        "candidate_name": "Iván Cepeda",
        "bloc": "izquierda",
        "country": "CO",
        "election_year": 2026,
        "source_priority": "A",
        "source_type": "program",
        "document_level": "program",
        "document_type": "government_program",
        "access_method": "direct_pdf",
        "title": "Plan de GOB",
        "url": "https://movimientopactohistorico.co/docs/programa-gobierno-2026-2030.pdf",
        "file_type": "pdf",
        "local_filename": "programa_gobierno_cepeda.pdf",
        "is_official": True,
        "status": "pending",
        "notes": "Programa completo o PDF enlazado internamente",
        "analysis_eligibility": "core",
        "extraction_method": "pymupdf",
        "quality_flag": "clean",
    },
    {
        "candidate_id": "paloma_valencia",
        "candidate_name": "Paloma Valencia",
        "bloc": "derecha",
        "country": "CO",
        "election_year": 2026,
        "source_priority": "A",
        "source_type": "program",
        "document_level": "program",
        "document_type": "government_program",
        "access_method": "direct_pdf",
        "title": "Propuestas oficiales",
        "url": "https://palomavalencia.com/propuestas.html",
        "file_type": "html",
        "local_filename": "propuestas.html",
        "is_official": True,
        "status": "pending",
        "notes": "Página programática oficial; no necesariamente equivale a programa integral",
        "analysis_eligibility": "core",
        "extraction_method": "none",
        "quality_flag": "none",
    },
    {
        "candidate_id": "sergio_fajardo",
        "candidate_name": "Sergio Fajardo",
        "bloc": "centro",
        "country": "CO",
        "election_year": 2026,
        "source_priority": "A",
        "source_type": "pdf",
        "document_level": "program",
        "document_type": "government_program",
        "access_method": "google_drive_direct",
        "title": "Programa de Gobierno",
        "url": "https://drive.google.com/uc?export=download&id=1b0JOU1qalqmih9YdYbuWIDWQEAAvYWn7",
        "file_type": "pdf",
        "local_filename": "programa_gobierno_fajardo.pdf",
        "is_official": True,
        "status": "pending",
        "notes": "PDF enlazado desde la web oficial vía Google Drive",
        "analysis_eligibility": "core",
        "extraction_method": "pymupdf",
        "quality_flag": "clean",
    },
    {
        "candidate_id": "claudia_lopez",
        "candidate_name": "Claudia López",
        "bloc": "centro",
        "country": "CO",
        "election_year": 2026,
        "source_priority": "A",
        "source_type": "pdf",
        "document_level": "program",
        "document_type": "government_program",
        "access_method": "direct_pdf",
        "title": "Programa de Gobierno",
        "url": "https://claudia-lopez.com/wp-content/uploads/2026/02/Programa-de-Gobierno-Claudia-Lopez.pdf",
        "file_type": "pdf",
        "local_filename": "programa_gobierno_claudia_lopez.pdf",
        "is_official": True,
        "status": "pending",
        "notes": "PDF oficial completo",
        "analysis_eligibility": "core",
        "extraction_method": "ocr",
        "quality_flag": "ocr_noisy",
    },
    {
        "candidate_id": "abelardo_de_la_espriella",
        "candidate_name": "Abelardo de la Espriella",
        "bloc": "derecha",
        "country": "CO",
        "election_year": 2026,
        "source_priority": "A",
        "source_type": "pdf",
        "document_level": "program",
        "document_type": "government_program",
        "access_method": "direct_pdf",
        "title": "Defensores de la Patria",
        "url": "https://defensoresdelapatria.com/",
        "file_type": "pdf",
        "local_filename": "programa.pdf",
        "is_official": True,
        "status": "pending",
        "notes": "Documento programático descargable",
        "analysis_eligibility": "core",
        "extraction_method": "none",
        "quality_flag": "none",
    },
    {
        "candidate_id": "luis_gilberto_murillo",
        "candidate_name": "Luis Gilberto Murillo",
        "bloc": "centro",
        "country": "CO",
        "election_year": 2026,
        "source_priority": "C",
        "source_type": "unknown",
        "document_level": "missing",
        "document_type": "unknown",
        "access_method": "manual_pending",
        "title": "Fuente programática pendiente",
        "url": "",
        "file_type": "unknown",
        "local_filename": "",
        "is_official": False,
        "status": "missing",
        "notes": "Candidatura identificada, pero sin documento programático oficial cargado aún",
        "analysis_eligibility": "core",
        "extraction_method": "none",
        "quality_flag": "none",
    },
    {
        "candidate_id": "roy_barreras",
        "candidate_name": "Roy Barreras",
        "bloc": "centro-izquierda",
        "country": "CO",
        "election_year": 2026,
        "source_priority": "C",
        "source_type": "unknown",
        "document_level": "missing",
        "document_type": "unknown",
        "access_method": "manual_pending",
        "title": "Fuente programática pendiente",
        "url": "",
        "file_type": "unknown",
        "local_filename": "",
        "is_official": False,
        "status": "missing",
        "notes": "Candidatura identificada, pero sin documento programático oficial cargado aún",
        "analysis_eligibility": "core",
        "extraction_method": "none",
        "quality_flag": "none",
    },
]


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    for candidate in CANDIDATES:
        (RAW_DIR / candidate.candidate_id).mkdir(parents=True, exist_ok=True)


def write_seed_manifest() -> None:
    ensure_dirs()

    with MANIFEST_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(SEED_SOURCES)


if __name__ == "__main__":
    write_seed_manifest()
    print(f"Manifest creado en: {MANIFEST_FILE}")
