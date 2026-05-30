"""
Resume parsing route for uploaded resume files.
"""

from __future__ import annotations

import asyncio
import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.ai_resume_parser import parse_resume_with_ai
from app.services.resume_parser import parse_json_resume, parse_pdf_resume, parse_text_resume

router = APIRouter(tags=["resume"])


def _resume_quality_score(resume_input: dict) -> int:
    if not isinstance(resume_input, dict):
        return 0
    personal = resume_input.get("personal") or {}
    score = 0
    if personal.get("name"):
        score += 2
    if personal.get("title"):
        score += 2
    score += min(len(resume_input.get("education", [])), 2)
    score += min(len(resume_input.get("experience", [])), 3)
    score += min(len(resume_input.get("projects", [])), 3)
    score += min(len(resume_input.get("skills", [])) // 4, 3)
    return score


@router.post("/api/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        mode = os.getenv("RESUME_PARSER_MODE", "hybrid").lower()
        ai_timeout = int(os.getenv("RESUME_AI_TIMEOUT_SECONDS", "90"))

        if filename.endswith(".pdf"):
            rule_based = parse_pdf_resume(content)
            if mode in {"ai", "hybrid"}:
                try:
                    parsed = await asyncio.wait_for(
                        asyncio.to_thread(
                            parse_resume_with_ai,
                            rule_based.get("_raw_resume_text", ""),
                        ),
                        timeout=ai_timeout,
                    )
                    if _resume_quality_score(parsed) < _resume_quality_score(rule_based):
                        parsed = rule_based
                except Exception:
                    if mode == "ai":
                        raise
                    parsed = rule_based
            else:
                parsed = rule_based
            fmt = "pdf"
        elif filename.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")
            rule_based = parse_text_resume(text)
            if mode in {"ai", "hybrid"}:
                try:
                    parsed = await asyncio.wait_for(
                        asyncio.to_thread(
                            parse_resume_with_ai,
                            rule_based.get("_raw_resume_text", text),
                        ),
                        timeout=ai_timeout,
                    )
                    if _resume_quality_score(parsed) < _resume_quality_score(rule_based):
                        parsed = rule_based
                except Exception:
                    if mode == "ai":
                        raise
                    parsed = rule_based
            else:
                parsed = rule_based
            fmt = "txt"
        elif filename.endswith(".json"):
            parsed = parse_json_resume(content.decode("utf-8", errors="ignore"))
            fmt = "json"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Use .pdf, .txt, or .json.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse resume: {exc}",
        ) from exc

    return {
        "status": "ok",
        "format": fmt,
        "resume_input": parsed,
    }
