"""
Editing routes — conversational editing of a generated website.

- ``POST /api/edit`` → apply a natural-language edit to the current file map
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import EditRequest, EditResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["edit"])

# Ensure the crew package is importable
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_CREW_SRC_DIR = _BACKEND_DIR / "website_maker" / "src"


def _ensure_crew_on_path() -> None:
    src = str(_CREW_SRC_DIR)
    if src not in sys.path:
        sys.path.insert(0, src)


# ---------------------------------------------------------------------------
# POST /api/edit
# ---------------------------------------------------------------------------

@router.post("/api/edit", response_model=EditResponse)
async def edit_website(request: EditRequest) -> EditResponse:
    """Apply a conversational edit to the current website files.

    The editing agent receives:
    - The edit prompt describing what to change
    - The current file map so it knows the existing code
    - (Optional) resume context for data-aware edits

    It returns an updated file map and a human-readable changes summary.
    """

    import asyncio

    try:
        result = await asyncio.to_thread(
            _run_editing_agent,
            edit_prompt=request.edit_prompt,
            current_files=request.current_files,
            resume_input=request.resume_input,
        )
        return result

    except Exception as exc:
        logger.error("Editing failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Editing agent failed: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _run_editing_agent(
    edit_prompt: str,
    current_files: dict[str, str],
    resume_input: dict[str, Any] | None,
) -> EditResponse:
    """Blocking call to the CrewAI editing agent (runs in a thread)."""

    _ensure_crew_on_path()

    from website_maker.crew import ResumeGalaCrew  # noqa: E402

    crew_instance = ResumeGalaCrew()

    # Build the inputs for the editing task.
    # The editing_task in the crew has no pre-defined context, so we pass
    # everything it needs through the inputs dict.
    inputs: dict[str, Any] = {
        "edit_prompt": edit_prompt,
        "current_files": json.dumps(current_files),
    }
    if resume_input:
        inputs["resume_input"] = resume_input

    # The editing agent is a standalone agent; we create a minimal crew
    # with just that agent + its task.
    editing_agent = crew_instance.editing_agent()
    editing_task = crew_instance.editing_task()

    from crewai import Crew, Process

    mini_crew = Crew(
        agents=[editing_agent],
        tasks=[editing_task],
        process=Process.sequential,
        verbose=True,
    )

    result = mini_crew.kickoff(inputs=inputs)
    raw = str(result)

    # Parse the editing agent's output
    updated_files, summary = _parse_edit_output(raw, current_files)

    return EditResponse(
        updated_files=updated_files,
        changes_summary=summary,
    )


def _parse_edit_output(
    raw: str, fallback_files: dict[str, str]
) -> tuple[dict[str, str], str]:
    """Parse the editing agent's output into (updated_files, summary).

    Expected format is a JSON object with ``files`` and ``summary`` keys, but
    we handle graceful fallback.
    """

    # Attempt 1: parse entire output as JSON
    for candidate in [raw, raw[raw.find("{") : raw.rfind("}") + 1] if "{" in raw else []]:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                files = parsed.get("files") or parsed.get("updated_files") or parsed
                summary = parsed.get("summary") or parsed.get("changes_summary") or "Edit applied."

                # If 'files' is itself the whole dict (no wrapper), filter out non-file keys
                if isinstance(files, dict) and all(isinstance(v, str) for v in files.values()):
                    return files, str(summary)
        except (json.JSONDecodeError, TypeError):
            continue

    # Fallback: return original files unchanged with the raw output as summary
    logger.warning("Could not parse edit output — returning original files.")
    return fallback_files, f"Edit agent responded but output could not be parsed. Raw: {raw[:500]}"
