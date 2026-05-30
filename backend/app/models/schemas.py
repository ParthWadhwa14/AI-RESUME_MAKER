"""
Pydantic models for Resume Gala API request/response schemas.

Defines the data contracts between the Next.js frontend and the FastAPI backend,
including generation requests, edit requests, and job status tracking.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Resume data models
# ---------------------------------------------------------------------------

class ResumeInput(BaseModel):
    """Structured resume data provided by the user."""

    name: str = Field(..., description="Full name of the resume owner")
    title: str = Field(..., description="Professional title / headline")
    education: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of education entries (school, degree, year, etc.)",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="List of skill keywords",
    )
    projects: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of project entries (name, description, tech, link, etc.)",
    )
    experience: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of work-experience entries (company, role, dates, bullets, etc.)",
    )


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    """Payload sent by the frontend to kick off website generation."""

    resume_input: dict[str, Any] = Field(
        ..., description="Raw resume data dict (matches ResumeInput shape)"
    )
    user_prompt: str = Field(
        ...,
        description="Free-form prompt describing desired style / preferences",
    )
    github_url: Optional[str] = Field(
        None,
        description="Optional GitHub profile URL for enrichment",
    )
    linkedin_url: Optional[str] = Field(
        None,
        description="Optional LinkedIn profile URL for enrichment",
    )


class GenerateResponse(BaseModel):
    """Immediate response returned after a generation job is queued."""

    job_id: str = Field(..., description="Unique job identifier (UUID4)")
    status: str = Field("pending", description="Initial status of the job")
    files: Optional[dict[str, str]] = Field(
        None, description="Generated file map (available once completed)"
    )
    downloads: Optional[list[dict[str, str]]] = Field(
        None, description="Asset download manifest from the asset agent"
    )


# ---------------------------------------------------------------------------
# Editing
# ---------------------------------------------------------------------------

class EditRequest(BaseModel):
    """Payload for conversational editing of an already-generated site."""

    edit_prompt: str = Field(
        ..., description="Natural-language description of the edit"
    )
    current_files: dict[str, str] = Field(
        ..., description="Current file map (filename → code)"
    )
    resume_input: Optional[dict[str, Any]] = Field(
        None, description="Optional resume context for the editing agent"
    )


class EditResponse(BaseModel):
    """Response from the editing endpoint."""

    updated_files: dict[str, str] = Field(
        ..., description="Patched file map after applying the edit"
    )
    changes_summary: str = Field(
        ..., description="Human-readable summary of what changed"
    )


# ---------------------------------------------------------------------------
# Job tracking
# ---------------------------------------------------------------------------

class JobStatusEnum(str, Enum):
    """Possible states for an async generation job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatus(BaseModel):
    """Tracks the lifecycle of an async generation job."""

    job_id: str
    status: JobStatusEnum = JobStatusEnum.PENDING
    progress: int = Field(0, ge=0, le=100, description="Percentage progress")
    current_agent: Optional[str] = Field(
        None, description="Name of the agent currently executing"
    )
    files: Optional[dict[str, str]] = Field(
        None, description="Generated file map (available on completion)"
    )
    error: Optional[str] = Field(
        None, description="Error message if the job failed"
    )


# ---------------------------------------------------------------------------
# Portfolio CRUD
# ---------------------------------------------------------------------------

class PortfolioCreate(BaseModel):
    """Payload for saving a new portfolio."""
    title: str = Field(default="Untitled Portfolio", description="Portfolio display name")
    prompt: Optional[str] = Field(None, description="Generation prompt used")
    resume_data: Optional[dict[str, Any]] = Field(None, description="Resume input data")
    files: dict[str, str] = Field(..., description="Generated file map (filename → code)")
    job_id: Optional[str] = Field(None, description="Associated generation job ID")


class PortfolioUpdate(BaseModel):
    """Payload for updating an existing portfolio."""
    title: Optional[str] = None
    files: Optional[dict[str, str]] = None


class PortfolioResponse(BaseModel):
    """Portfolio data returned from the API."""
    id: str
    user_id: str
    title: str
    prompt: Optional[str] = None
    resume_data: Optional[dict[str, Any]] = None
    files: dict[str, str]
    job_id: Optional[str] = None
    created_at: str
    updated_at: str
