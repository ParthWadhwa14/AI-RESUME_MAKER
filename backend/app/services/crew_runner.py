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
from app.services.react_project_formatter import ReactProjectFormatter
from app.services.preflight_runner import PreflightError, PreflightRunner
from app.services.dev_server_manager import DevServerManager

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
        "rate limit",
        "429",
    ]
    return any(token in msg for token in retry_signals)


def _should_allow_full_restart_retry() -> bool:
    """Whether to retry the *entire* crew (expensive)."""
    val = (os.getenv("CREW_ALLOW_RESTART_RETRIES", "0") or "").strip().lower()
    return val in {"1", "true", "yes", "on"}


class CrewRunner:
    """Runs the Resume Gala generation crew and tracks job progress."""

    @staticmethod
    def _persist_local_snapshot(
        *,
        job_id: str,
        resume_input: dict[str, Any],
        user_prompt: str,
        files: dict[str, str] | None,
        title_hint: str | None = None,
        failure_note: str | None = None,
    ) -> None:
        """Best-effort persistence of generated files so output is never lost."""
        if not files:
            return
        try:
            from app.services.local_store.store import LocalPortfolioStore

            store = LocalPortfolioStore()
            title = (
                title_hint
                or (resume_input.get("personal", {}) or {}).get("name")
                or resume_input.get("name")
                or "Generated Portfolio"
            )
            meta = store.create(
                title=title,
                prompt=user_prompt,
                resume_data=resume_input,
                files=files,
                job_id=job_id,
            )
            if failure_note:
                # annotate meta.json with failure info (non-fatal)
                try:
                    import json
                    from pathlib import Path

                    backend_dir = Path(__file__).resolve().parents[2]
                    base = backend_dir / "local_portfolios"
                    # find folder by prefix
                    for d in sorted(base.glob(f"{meta.id}-*")):
                        mf = d / "meta.json"
                        if mf.is_file():
                            obj = json.loads(mf.read_text(encoding="utf-8"))
                            obj["failure_note"] = failure_note
                            mf.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
                            break
                except Exception:
                    pass
        except Exception as exc:
            logger.warning("Local snapshot persistence failed for job %s: %s", job_id, exc)

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
            timeout_seconds = int(os.getenv("CREW_JOB_TIMEOUT_SECONDS", "600"))

            # Restart retries are expensive and feel like "it restarted".
            # Default to 0 unless explicitly enabled.
            allow_restarts = _should_allow_full_restart_retry()
            max_restarts = int(os.getenv("CREW_MAX_RETRIES", "0" if not allow_restarts else "1"))
            fallback_model = os.getenv("CREW_FALLBACK_MODEL", "").strip()

            files: dict[str, str] | None = None
            last_exc: Exception | None = None

            for attempt in range(max_restarts + 1):
                try:
                    if attempt > 0 and fallback_model:
                        os.environ["MODEL"] = fallback_model
                        logger.warning(
                            "Retrying job %s with fallback model '%s' (full restart attempt %d/%d)",
                            job_id,
                            fallback_model,
                            attempt + 1,
                            max_restarts + 1,
                        )
                    elif attempt > 0:
                        logger.warning(
                            "Retrying job %s with same model (full restart attempt %d/%d)",
                            job_id,
                            attempt + 1,
                            max_restarts + 1,
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

                    # If we already have some files from a prior run (rare), try the fast alternate path.
                    # More importantly: if the error is retryable (timeout/rate-limit), DO NOT restart the
                    # whole crew by default — instead fail fast with guidance.
                    if isinstance(exc, asyncio.TimeoutError) or _is_retryable_llm_error(exc):
                        if attempt < max_restarts and allow_restarts:
                            await asyncio.sleep(min(2 * (attempt + 1), 8))
                            continue

                        raise RuntimeError(
                            "Generation hit a retryable upstream error (timeout/rate-limit). "
                            "To avoid full restarts, retries are disabled by default. "
                            "If you want automatic restarts, set CREW_ALLOW_RESTART_RETRIES=1 and CREW_MAX_RETRIES=1. "
                            f"Original error: {exc}"
                        ) from exc

                    raise

            if files is None and last_exc:
                raise last_exc

            downloads = files.pop("__downloads__", None)
            if downloads and isinstance(downloads, list):
                logger.info("Processing %d asset downloads …", len(downloads))
                asset_map = await AssetBridge.process_downloads(downloads)
                files.update(asset_map)

            files = ReactProjectFormatter.normalize(files)

            # Persist an early snapshot (post-normalization) so we never lose output.
            CrewRunner._persist_local_snapshot(
                job_id=job_id,
                resume_input=resume_input,
                user_prompt=user_prompt,
                files=files,
                title_hint="(snapshot) " + (
                    (resume_input.get("personal", {}) or {}).get("name")
                    or resume_input.get("name")
                    or "Generated Portfolio"
                ),
            )

            jobs_store[job_id] = JobStatus(
                job_id=job_id,
                status=JobStatusEnum.PROCESSING,
                progress=95,
                current_agent="preflight",
            )

            try:
                files = await PreflightRunner.run_preflight(files=files, job_id=job_id)
            except PreflightError as exc:
                # Save failing output snapshot for debugging before attempting fixup.
                CrewRunner._persist_local_snapshot(
                    job_id=job_id,
                    resume_input=resume_input,
                    user_prompt=user_prompt,
                    files=files,
                    title_hint="(preflight-failed) " + (
                        (resume_input.get("personal", {}) or {}).get("name")
                        or resume_input.get("name")
                        or "Generated Portfolio"
                    ),
                    failure_note=str(exc),
                )

                # Alternate path: attempt a cheap "fix-only" run (checking/testing) instead of restarting full crew.
                try:
                    jobs_store[job_id] = JobStatus(
                        job_id=job_id,
                        status=JobStatusEnum.PROCESSING,
                        progress=96,
                        current_agent="preflight_fixup",
                    )
                    files = await asyncio.wait_for(
                        asyncio.to_thread(CrewRunner._run_fast_fixup_sync, files, job_id, jobs_store),
                        timeout=90,
                    )
                    files = ReactProjectFormatter.normalize(files)

                    # Save post-fix snapshot too.
                    CrewRunner._persist_local_snapshot(
                        job_id=job_id,
                        resume_input=resume_input,
                        user_prompt=user_prompt,
                        files=files,
                        title_hint="(fixup-snapshot) " + (
                            (resume_input.get("personal", {}) or {}).get("name")
                            or resume_input.get("name")
                            or "Generated Portfolio"
                        ),
                    )

                    files = await PreflightRunner.run_preflight(files=files, job_id=job_id)
                except Exception:
                    detail = str(exc)
                    if getattr(exc, "issues", None):
                        detail += "\n" + "\n".join(f"- {i.code}: {i.message}" for i in exc.issues)
                    raise RuntimeError("Preflight failed and fixup could not recover.\n" + detail) from exc

            # Persist locally so the last run is always available on disk.
            preview_url = None
            try:
                from app.services.local_store.store import LocalPortfolioStore

                store = LocalPortfolioStore()
                portfolio_title = (
                    (resume_input.get("personal", {}) or {}).get("name")
                    or resume_input.get("name")
                    or "Generated Portfolio"
                )
                meta = store.create(
                    title=portfolio_title,
                    prompt=user_prompt,
                    resume_data=resume_input,
                    files=files or {},
                    job_id=job_id,
                )

                # Start a live Vite dev server for the generated project
                try:
                    project_dir = store._portfolio_dir(meta.id) / "files"
                    if project_dir.is_dir():
                        manager = DevServerManager.instance()
                        preview_url = await manager.start_server(
                            job_id=job_id,
                            project_dir=project_dir,
                        )
                        logger.info("Live preview for job %s at %s", job_id, preview_url)
                except Exception as _preview_exc:
                    logger.warning(
                        "Job %s completed but live preview failed to start: %s",
                        job_id, _preview_exc,
                    )
            except Exception as _persist_exc:
                logger.warning("Job %s completed but local persistence failed: %s", job_id, _persist_exc)

            jobs_store[job_id] = JobStatus(
                job_id=job_id,
                status=JobStatusEnum.COMPLETED,
                progress=100,
                files=files,
                preview_url=preview_url,
            )

            logger.info("Job %s completed with %d files (preview: %s)", job_id, len(files), preview_url or "N/A")

        except asyncio.TimeoutError:
            timeout_seconds = int(os.getenv("CREW_JOB_TIMEOUT_SECONDS", "600"))
            msg = (
                f"Generation timed out after {timeout_seconds}s. "
                "Try a shorter prompt, disable research/assets, or use a faster model."
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

    @staticmethod
    def _run_fast_fixup_sync(
        files: dict[str, str],
        job_id: str,
        jobs_store: dict[str, JobStatus],
    ) -> dict[str, str]:
        """Small alternate path that tries to fix obvious build/runtime issues.

        Purpose: avoid re-running the entire generation crew after a near-complete output.
        Runs ONLY checking + testing steps (prompted to patch the existing file map).
        """

        _ensure_crew_on_path()
        _normalize_model_env_for_provider()

        from website_maker.crew import ResumeGalaCrew  # noqa: E402
        from crewai import Crew, Process  # type: ignore

        # Keep job progress moving for UI.
        jobs_store[job_id] = JobStatus(
            job_id=job_id,
            status=JobStatusEnum.PROCESSING,
            progress=97,
            current_agent="fast_fixup",
        )

        crew_instance = ResumeGalaCrew()
        checking_task = crew_instance.checking_task()
        testing_task = crew_instance.testing_task()

        # Only the agents needed for these tasks.
        checking_agent = crew_instance.checking_agent()
        testing_agent = crew_instance.testing_agent()

        mini_crew = Crew(
            agents=[checking_agent, testing_agent],
            tasks=[checking_task, testing_task],
            process=Process.sequential,
            verbose=True,
            max_rpm=15,
        )

        # Provide the existing files via the standard input channel.
        result = mini_crew.kickoff(
            inputs={
                "resume_input": {},
                "user_prompt": "Preflight fixup mode: DO NOT change content. Only fix build/runtime problems. Return final_files.",
                "current_files": json.dumps(files),
            }
        )

        patched = CrewRunner._parse_crew_output(result)

        # If the mini crew returned only a raw wrapper, fall back to original files.
        if "index.html" in patched and len(patched) == 1 and patched.get("index.html", "").strip().startswith("{") is False:
            return files

        return {str(k): str(v) for k, v in patched.items()}
