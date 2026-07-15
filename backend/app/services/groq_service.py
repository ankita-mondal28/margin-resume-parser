"""
Talks to Groq's chat-completions API to turn raw resume text into
structured JSON (contact info, skills, education, experience, a score,
and suggested roles).

The API key is read once at startup from settings (which itself reads
it from the environment / .env file) and is never logged, echoed back
to the client, or included in error messages.
"""

import json
import logging

from fastapi import HTTPException
from groq import Groq

from app.config import get_settings

logger = logging.getLogger("resume_parser.groq")

SYSTEM_PROMPT = """You are a meticulous resume-analysis assistant.

You will be given the raw extracted text of a resume, which may contain
OCR noise or odd spacing. Read past formatting artifacts and infer the
actual content.

Respond with ONLY a single valid JSON object (no markdown fences, no
commentary) matching exactly this shape:

{
  "full_name": string | null,
  "email": string | null,
  "phone": string | null,
  "location": string | null,
  "links": string[],
  "summary": string,               // 2-3 sentence third-person summary of the candidate
  "skills": string[],              // deduplicated, concise skill names
  "education": [
    {"institution": string|null, "degree": string|null, "field_of_study": string|null,
     "start_date": string|null, "end_date": string|null}
  ],
  "experience": [
    {"company": string|null, "title": string|null, "start_date": string|null,
     "end_date": string|null, "description": string|null}
  ],
  "resume_score": integer,          // 0-100 overall quality score
  "score_breakdown": string,        // one short sentence explaining the score, encouraging in tone
  "suggested_roles": [
    {"title": string, "reason": string}   // 2-4 realistic job titles this person is suited for
  ]
}

Scoring rubric (weigh roughly equally): clarity of contact info, strength
and specificity of experience descriptions (quantified impact is good),
skills relevance and breadth, education completeness, and overall
formatting/readability inferred from the text structure. Be honest but
constructive — score_breakdown should sound like encouraging, specific
feedback, never harsh.

If a field cannot be determined, use null (or an empty array), never
invent information that is not supported by the text."""


def analyze_resume(resume_text: str) -> dict:
    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)

    base_kwargs = dict(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Resume text:\n\n{resume_text}"},
        ],
        temperature=0.2,
        max_completion_tokens=2000,
        response_format={"type": "json_object"},
    )
    # gpt-oss / reasoning models "think" before answering. We don't need deep
    # reasoning for a straightforward extraction task, and we need the
    # reasoning kept OUT of `message.content` so it doesn't corrupt the JSON.
    # Not every model on Groq accepts these two fields, so if the configured
    # model rejects them, we transparently retry without them instead of
    # hard-failing the request.
    reasoning_kwargs = dict(reasoning_effort="low", reasoning_format="hidden")

    try:
        try:
            completion = client.chat.completions.create(**base_kwargs, **reasoning_kwargs)
        except Exception as exc:
            if "reasoning" in str(exc).lower() or "unknown parameter" in str(exc).lower():
                logger.info("Model %s doesn't accept reasoning params, retrying without them", settings.groq_model)
                completion = client.chat.completions.create(**base_kwargs)
            else:
                raise
    except Exception as exc:
        logger.error("Groq API call failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="Couldn't reach the AI service right now. Please try again in a moment.",
        ) from exc

    raw_content = completion.choices[0].message.content

    try:
        data = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Groq returned non-JSON content")
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unexpected response. Please try again.",
        ) from exc

    return _coerce_shape(data)


def _coerce_shape(data: dict) -> dict:
    """Fills in any missing keys with safe defaults so schema validation never
    fails just because the model omitted an optional field."""
    defaults = {
        "full_name": None,
        "email": None,
        "phone": None,
        "location": None,
        "links": [],
        "summary": None,
        "skills": [],
        "education": [],
        "experience": [],
        "resume_score": 0,
        "score_breakdown": None,
        "suggested_roles": [],
    }
    defaults.update({k: v for k, v in data.items() if k in defaults})

    score = defaults.get("resume_score")
    if not isinstance(score, int):
        try:
            defaults["resume_score"] = max(0, min(100, int(score)))
        except (TypeError, ValueError):
            defaults["resume_score"] = 0
    else:
        defaults["resume_score"] = max(0, min(100, score))

    for field in ("suggested_roles", "education", "experience"):
        defaults[field] = _normalize_list_of_dicts(defaults.get(field))

    return defaults


def _normalize_list_of_dicts(value) -> list:
    if not isinstance(value, list):
        return []
    normalized = []
    for item in value:
        if isinstance(item, dict):
            normalized.append(item)
        elif isinstance(item, str):
            try:
                parsed = json.loads(item)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(parsed, dict):
                normalized.append(parsed)
    return normalized
