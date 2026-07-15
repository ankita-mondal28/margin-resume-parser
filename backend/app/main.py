import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.routers.parse import limiter, router as parse_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("resume_parser")

settings = get_settings()

app = FastAPI(
    title="Resume Parser API",
    description="Extracts structured data, a quality score, and role suggestions from resumes using Groq.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(parse_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak internal error details (stack traces, file paths, etc.)
    # to the client — log them server-side and return a generic message.
    if isinstance(exc, HTTPException):
        raise exc
    logger.exception("Unhandled error while processing request")
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on our end. Please try again."})
