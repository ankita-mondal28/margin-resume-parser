import logging
import os
import tempfile

from fastapi import APIRouter, File, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.models.schemas import ParseResponse
from app.services import extractor
from app.services.groq_service import analyze_resume
from app.services.security import enforce_size_limit, validate_and_prepare

logger = logging.getLogger("resume_parser.parse")

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/parse", response_model=ParseResponse)
@limiter.limit(lambda: f"{get_settings().rate_limit_per_minute}/minute")
async def parse_resume(request: Request, file: UploadFile = File(...)) -> ParseResponse:
    settings = get_settings()

    safe_upload = validate_and_prepare(file)

    contents = await file.read()
    enforce_size_limit(len(contents), settings.max_file_size_bytes)

    # Every upload gets its own temp directory, guaranteed to be wiped
    # (including the raw resume bytes) as soon as this request finishes,
    # whether it succeeds or fails.
    with tempfile.TemporaryDirectory(prefix="resume_") as tmp_dir:
        tmp_path = os.path.join(tmp_dir, safe_upload.safe_filename)
        with open(tmp_path, "wb") as f:
            f.write(contents)

        resume_text = extractor.extract_text(tmp_path, safe_upload.extension)
        # tmp_dir and its contents are deleted automatically on exit here.

    analysis = analyze_resume(resume_text)
    analysis["original_filename"] = safe_upload.original_filename

    logger.info("Parsed resume '%s' (%d chars extracted)", safe_upload.original_filename, len(resume_text))

    return ParseResponse(**analysis)
