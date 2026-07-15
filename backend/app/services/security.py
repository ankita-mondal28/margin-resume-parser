"""
Security helpers for handling untrusted file uploads.

Principles applied here:
- Allow-list extensions and content-types, never block-list.
- Never trust the client-supplied filename for anything other than
  display; a random server-generated name is used on disk.
- Enforce a hard size cap before any parsing library touches the file,
  to avoid decompression-bomb / resource-exhaustion style issues.
- Uploaded files always land in a per-request temp directory that is
  guaranteed to be deleted after the request finishes (see routers/parse.py).
"""

import os
import uuid
from dataclasses import dataclass

from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg"}

# Real-world browsers/OSes are inconsistent about the exact content-type they
# report (e.g. some send "application/octet-stream" for a perfectly valid
# .docx). We use an allow-list of plausible types per extension rather than
# a strict single-value match, so we still reject obvious mismatches (e.g. an
# .html file renamed to .pdf reporting "text/html") without false-rejecting
# legitimate uploads. The real gatekeepers are the extension allow-list, the
# size cap, and the fact that the parsing libraries themselves will reject
# malformed content.
PLAUSIBLE_CONTENT_TYPES = {
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
        "application/zip",
    },
    ".png": {"image/png", "application/octet-stream"},
    ".jpg": {"image/jpeg", "application/octet-stream"},
    ".jpeg": {"image/jpeg", "application/octet-stream"},
}


@dataclass
class SafeUpload:
    safe_filename: str
    extension: str
    original_filename: str


def validate_and_prepare(file: UploadFile) -> SafeUpload:
    """
    Validates the uploaded file's extension/content-type and returns a
    randomly generated, filesystem-safe filename to save it as.
    Raises HTTPException(400/415) on anything suspicious.
    """
    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="File has no extension.")

    original_filename = os.path.basename(file.filename)  # strip any path components
    extension = os.path.splitext(original_filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    declared_content_type = (file.content_type or "").lower()
    allowed_types = PLAUSIBLE_CONTENT_TYPES[extension]
    if declared_content_type and declared_content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail="File content-type does not match its extension.",
        )

    safe_filename = f"{uuid.uuid4().hex}{extension}"
    return SafeUpload(safe_filename=safe_filename, extension=extension, original_filename=original_filename)


def enforce_size_limit(size_bytes: int, max_bytes: int) -> None:
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed size is {max_bytes // (1024 * 1024)} MB.",
        )
