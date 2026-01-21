"""
DOI lookup service.
"""
from typing import List
import os
import re
import uuid

import httpx

from app.config import settings
from app.services.ingestion_service import ingest_pdf
from app.utils.doi_fetcher import fetch_doi_metadata, normalize_doi
from app.models.schemas import DoiLookupResult, PaperResponse


def lookup_dois(dois: List[str], max_items: int = 5) -> List[DoiLookupResult]:
    unique_dois = []
    seen = set()
    for doi in dois:
        normalized = normalize_doi(doi)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_dois.append(normalized)
        if len(unique_dois) >= max_items:
            break

    results: List[DoiLookupResult] = []
    for doi in unique_dois:
        data = fetch_doi_metadata(doi)
        results.append(DoiLookupResult(**data))
    return results


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("._-")
    return cleaned or "paper"


def import_doi(
    doi: str,
    workspace_id: str,
    user_id: str,
) -> PaperResponse:
    normalized = normalize_doi(doi)
    if not normalized:
        raise ValueError("Invalid DOI")

    metadata = fetch_doi_metadata(normalized)
    if metadata.get("error"):
        raise ValueError(metadata["error"])

    pdf_url = metadata.get("pdf_url")
    if not pdf_url:
        raise ValueError("No open-access PDF found for this DOI")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(pdf_url)
            if response.status_code != 200:
                raise ValueError("Failed to download PDF")
            pdf_bytes = response.content
    except Exception as exc:
        raise ValueError(f"Failed to download PDF: {str(exc)}") from exc

    if len(pdf_bytes) > settings.max_upload_size:
        raise ValueError("Downloaded PDF exceeds maximum allowed size")

    paper_id = str(uuid.uuid4())
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"{paper_id}.pdf")
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    original_name = metadata.get("title") or normalized
    original_filename = f"{_safe_filename(original_name)}.pdf"

    try:
        return ingest_pdf(
            pdf_path=file_path,
            paper_id=paper_id,
            workspace_id=workspace_id,
            user_id=user_id,
            original_filename=original_filename,
        )
    except Exception as exc:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise exc
