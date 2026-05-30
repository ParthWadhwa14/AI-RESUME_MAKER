"""
Generation routes — website generation with async job tracking.

- ``POST /api/generate``            → queue a new generation job
- ``GET  /api/generate/status/{id}`` → poll job progress
- ``GET  /api/download/{id}``       → download the finished site as a ZIP
"""

from __future__ import annotations

import asyncio
import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.models.schemas import (
    GenerateRequest,
    GenerateResponse,
    JobStatus,
    JobStatusEnum,
)
from app.services.crew_runner import CrewRunner
from app.services.profile_enricher import ProfileEnricher
from app.services.zip_builder import ZipBuilder

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generate"])

# ---------------------------------------------------------------------------
# In-memory job store — shared across the process lifetime.
# In production you'd swap this for Redis / a DB.
# ---------------------------------------------------------------------------
jobs: dict[str, JobStatus] = {}


def _has_meaningful_resume_data(resume_input: dict) -> bool:
    if not isinstance(resume_input, dict):
        return False
    personal = resume_input.get("personal") or {}
    if personal.get("name") or personal.get("title"):
        return True
    if resume_input.get("name") or resume_input.get("title"):
        return True
    for key in ("education", "experience", "skills", "projects"):
        if isinstance(resume_input.get(key), list) and len(resume_input.get(key)) > 0:
            return True
    if resume_input.get("_raw_resume_text"):
        return True
    return False


# ---------------------------------------------------------------------------
# POST /api/generate
# ---------------------------------------------------------------------------

@router.post("/api/generate", response_model=GenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_website(request: GenerateRequest) -> GenerateResponse:
    """Accept a generation request, queue it in the background, and return a job ID.

    The caller should poll ``GET /api/generate/status/{job_id}`` until the job
    reaches ``completed`` or ``failed``.
    """

    if not _has_meaningful_resume_data(request.resume_input):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Resume data is empty. Please fill the form or upload/parse your resume before generating."
            ),
        )

    job_id = str(uuid4())

    # Initialise the job entry
    jobs[job_id] = JobStatus(
        job_id=job_id,
        status=JobStatusEnum.PENDING,
        progress=0,
    )

    # Fire-and-forget background task
    enriched_resume_input = await ProfileEnricher.enrich(
        resume_input=request.resume_input,
        github_url=request.github_url,
        linkedin_url=request.linkedin_url,
    )

    asyncio.create_task(
        CrewRunner.run_generation(
            resume_input=enriched_resume_input,
            user_prompt=request.user_prompt,
            job_id=job_id,
            jobs_store=jobs,
        )
    )

    logger.info("Queued generation job %s", job_id)

    return GenerateResponse(
        job_id=job_id,
        status="pending",
    )


# ---------------------------------------------------------------------------
# GET /api/generate/status/{job_id}
# ---------------------------------------------------------------------------

@router.get("/api/generate/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str) -> JobStatus:
    """Return the current status of a generation job."""

    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )
    return job


# ---------------------------------------------------------------------------
# GET /api/download/{job_id}
# ---------------------------------------------------------------------------

@router.get("/api/download/{job_id}")
async def download_zip(job_id: str) -> Response:
    """Return the generated website as a downloadable ZIP archive.

    Only available once the job status is ``completed``.
    """

    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    if job.status != JobStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is not completed yet (current status: {job.status.value})",
        )

    if not job.files:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job completed but no files were generated",
        )

    zip_bytes = ZipBuilder.build_zip(job.files, project_name="resume-gala-site")

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="resume-gala-{job_id[:8]}.zip"',
        },
    )
