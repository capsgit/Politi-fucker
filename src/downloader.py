import csv
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
MANIFEST_FILE = BASE_DIR / "data" / "manifests" / "sources.csv"


def filename_from_url(url: str, fallback: str = "document") -> str:
    if not url:
        return fallback
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name if name else fallback


def download_file(url: str, output_path: Path) -> None:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; politi-fucker/0.1)"}

    response = requests.get(url, headers=headers, timeout=60)

    if "drive.google.com" in url:
        # Google drive sometimes requires confirm token
        if "text/html" in response.headers.get("content-type", ""):
            print("Google Drive warning page detected")

    response.raise_for_status()

    output_path.write_bytes(response.content)


def run() -> None:
    with MANIFEST_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            url = row["url"].strip()
            candidate_id = row["candidate_id"]

            if not url:
                print(f"[SKIP] {candidate_id}: sin URL")
                continue

            preferred_name = row.get("local_filename", "").strip()
            fallback_name = (
                "index.html" if row.get("file_type") == "html" else "document"
            )
            filename = preferred_name or filename_from_url(url, fallback=fallback_name)

            output_dir = RAW_DIR / candidate_id
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename

            try:
                if output_path.exists():
                    print(f"[SKIP] {candidate_id}: ya existe {output_path.name}")
                    continue

                download_file(url, output_path)
                print(f"[OK] {candidate_id}: {output_path.name}")
            except Exception as exc:
                print(f"[ERROR] {candidate_id}: {exc}")


if __name__ == "__main__":
    run()
