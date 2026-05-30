"""
CrewRunner — Orchestrates the CrewAI generation crew in a background thread.

This service is the bridge between the FastAPI route layer and the CrewAI
``ResumeGalaCrew``.  It:

1. Manipulates ``sys.path`` so the ``website_maker`` package is importable.
2. Instantiates and kicks off the generation crew.
3. Parses the crew output (expected JSON mapping filenames → code).
4. Optionally processes asset downloads via :class:`AssetBridge`.
5. Updates the shared in-memory ``jobs`` store throughout the lifecycle.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any

from app.models.schemas import JobStatus, JobStatusEnum
from app.services.asset_bridge import AssetBridge

logger = logging.getLogger(__name__)

# Resolve the path to the website_maker package once at import time.
_BACKEND_DIR = Path(__file__).resolve().parents[2]  # …/backend
_CREW_SRC_DIR = _BACKEND_DIR / "website_maker" / "src"


def _ensure_crew_on_path() -> None:
    """Add the crew source directory to ``sys.path`` if not already present."""
    src = str(_CREW_SRC_DIR)
    if src not in sys.path:
        sys.path.insert(0, src)
        logger.info("Added %s to sys.path", src)


def _normalize_model_env_for_provider() -> None:
    """
    Normalize model/provider env settings for litellm compatibility.
    """
    model = (os.getenv("MODEL") or "").strip()
    if not model:
        return

    # User-friendly alias -> canonical Groq model id expected by many litellm setups.
    if model == "groq/gpt-oss-120b":
        os.environ["MODEL"] = "groq/openai/gpt-oss-120b"

    model_after = (os.getenv("MODEL") or "").strip()
    if model_after.startswith("groq/"):
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        if groq_key:
            os.environ["OPENAI_API_KEY"] = groq_key
        # Ensure requests go to Groq OpenAI-compatible endpoint, not NVIDIA.
        os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
        os.environ.pop("NVIDIA_NIM_API_BASE", None)
    elif model_after.startswith("nvidia_nim/"):
        nvidia_key = os.getenv("NVIDIA_API_KEY", "").strip()
        if nvidia_key:
            os.environ["OPENAI_API_KEY"] = nvidia_key
        os.environ["OPENAI_API_BASE"] = "https://integrate.api.nvidia.com/v1"


def _is_retryable_llm_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    retry_signals = [
        "timeout",
        "error code: 504",
        "internalservererror: error code: 504",
        "gateway timeout",
        "service unavailable",
    ]
    return any(token in msg for token in retry_signals)


class CrewRunner:
    """Runs the Resume Gala generation crew and tracks job progress."""

    @staticmethod
    async def run_generation(
        resume_input: dict[str, Any],
        user_prompt: str,
        job_id: str,
        jobs_store: dict[str, JobStatus],
    ) -> None:
        """Execute the generation crew asynchronously.

        This method is designed to be called via ``asyncio.create_task`` from the
        route handler.  It runs the blocking CrewAI ``kickoff`` in a thread so
        the event loop stays responsive.

        Parameters
        ----------
        resume_input:
            Resume data dict matching the ``ResumeInput`` schema.
        user_prompt:
            Free-form prompt describing desired style/preferences.
        job_id:
            Unique job identifier (UUID4 string).
        jobs_store:
            Shared mutable dict that tracks all active job statuses.
        """

        # Mark as processing
        jobs_store[job_id] = JobStatus(
            job_id=job_id,
            status=JobStatusEnum.PROCESSING,
            progress=10,
            current_agent="planning_agent",
        )
        original_model = os.getenv("MODEL")

        try:
            timeout_seconds = int(os.getenv("CREW_JOB_TIMEOUT_SECONDS", "1200"))
            max_retries = int(os.getenv("CREW_MAX_RETRIES", "2"))
            fallback_model = os.getenv("CREW_FALLBACK_MODEL", "").strip()

            files: dict[str, str] | None = None
            last_exc: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0 and fallback_model:
                        os.environ["MODEL"] = fallback_model
                        logger.warning(
                            "Retrying job %s with fallback model '%s' (attempt %d/%d)",
                            job_id,
                            fallback_model,
                            attempt + 1,
                            max_retries + 1,
                        )
                    elif attempt > 0:
                        logger.warning(
                            "Retrying job %s with same model (attempt %d/%d)",
                            job_id,
                            attempt + 1,
                            max_retries + 1,
                        )

                    files = await asyncio.wait_for(
                        asyncio.to_thread(
                            CrewRunner._run_crew_sync, resume_input, user_prompt, job_id, jobs_store
                        ),
                        timeout=timeout_seconds,
                    )
                    break
                except Exception as exc:
                    last_exc = exc
                    if isinstance(exc, asyncio.TimeoutError) or _is_retryable_llm_error(exc):
                        if attempt < max_retries:
                            await asyncio.sleep(min(2 * (attempt + 1), 8))
                            continue
                    raise
            if files is None and last_exc:
                raise last_exc

            # Process any asset downloads embedded in the output
            downloads = files.pop("__downloads__", None)
            if downloads and isinstance(downloads, list):
                logger.info("Processing %d asset downloads …", len(downloads))
                asset_map = await AssetBridge.process_downloads(downloads)
                files.update(asset_map)

            jobs_store[job_id] = JobStatus(
                job_id=job_id,
                status=JobStatusEnum.COMPLETED,
                progress=100,
                files=files,
            )
            logger.info("Job %s completed with %d files", job_id, len(files))

        except asyncio.TimeoutError:
            timeout_seconds = int(os.getenv("CREW_JOB_TIMEOUT_SECONDS", "1200"))
            msg = (
                f"Generation timed out after {timeout_seconds}s. "
                "Please retry with a shorter prompt or a faster model."
            )
            logger.error("Job %s timed out after %ss", job_id, timeout_seconds)
            jobs_store[job_id] = JobStatus(
                job_id=job_id,
                status=JobStatusEnum.FAILED,
                progress=0,
                error=msg,
            )

        except Exception as exc:
            logger.error("Job %s failed: %s\n%s", job_id, exc, traceback.format_exc())
            jobs_store[job_id] = JobStatus(
                job_id=job_id,
                status=JobStatusEnum.FAILED,
                progress=0,
                error=str(exc),
            )
        finally:
            if original_model:
                os.environ["MODEL"] = original_model

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _run_crew_sync(
        resume_input: dict[str, Any],
        user_prompt: str,
        job_id: str,
        jobs_store: dict[str, JobStatus],
    ) -> dict[str, str]:
        """Blocking call — meant to run inside ``asyncio.to_thread``."""

        _ensure_crew_on_path()
        _normalize_model_env_for_provider()

        from website_maker.crew import ResumeGalaCrew  # noqa: E402 – deferred import

        # Update progress: crew instantiation
        jobs_store[job_id] = JobStatus(
            job_id=job_id,
            status=JobStatusEnum.PROCESSING,
            progress=20,
            current_agent="planning_agent",
        )

        crew_instance = ResumeGalaCrew()
        crew = crew_instance.generation_crew()

        # Update progress: kickoff
        jobs_store[job_id] = JobStatus(
            job_id=job_id,
            status=JobStatusEnum.PROCESSING,
            progress=30,
            current_agent="design_theme_agent",
        )

        result = crew.kickoff(
            inputs={
                "user_prompt": user_prompt,
                "resume_input": resume_input,
            }
        )

        # Update progress: parsing output
        jobs_store[job_id] = JobStatus(
            job_id=job_id,
            status=JobStatusEnum.PROCESSING,
            progress=90,
            current_agent="parsing_output",
        )

        return CrewRunner._parse_crew_output(result)

    @staticmethod
    def _parse_crew_output(result: Any) -> dict[str, str]:
        """Best-effort parse of the crew's raw output into a file map.

        The crew is expected to return a JSON string like::

            {"index.html": "<html>…", "src/App.jsx": "import …", …}

        If parsing fails, the raw output is wrapped in a single-file dict.
        """

        # Preferred path: use parsed output prepared by @after_kickoff in crew.py
        parsed_files = getattr(result, "_parsed_files", None)
        if isinstance(parsed_files, dict):
            return {str(k): str(v) for k, v in parsed_files.items()}

        raw: str = str(result)

        def _extract_file_map(parsed_obj: Any) -> dict[str, str] | None:
            if not isinstance(parsed_obj, dict):
                return None
            if "final_files" in parsed_obj and isinstance(parsed_obj.get("final_files"), dict):
                return {
                    str(k): str(v)
                    for k, v in parsed_obj["final_files"].items()
                }
            if all(isinstance(v, str) for v in parsed_obj.values()):
                return {str(k): str(v) for k, v in parsed_obj.items()}
            return None

        # Attempt 1: direct JSON parse
        try:
            parsed = json.loads(raw)
            extracted = _extract_file_map(parsed)
            if extracted is not None:
                return extracted
        except (json.JSONDecodeError, TypeError):
            pass

        # Attempt 2: look for JSON object within the raw string
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(raw[start : end + 1])
                extracted = _extract_file_map(parsed)
                if extracted is not None:
                    return extracted
            except (json.JSONDecodeError, TypeError):
                pass

        # Fallback: wrap raw output
        logger.warning("Could not parse crew output as JSON — wrapping raw output.")
        return {"index.html": raw}
