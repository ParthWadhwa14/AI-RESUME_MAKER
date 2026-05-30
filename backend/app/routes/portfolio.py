"""
Portfolio CRUD routes — save, list, get, update, and delete generated portfolios.

All endpoints require authentication via the ``get_current_user`` dependency.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import PortfolioCreate, PortfolioResponse, PortfolioUpdate
from app.routes.auth import UserInfo, get_current_user, _get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])


# ---------------------------------------------------------------------------
# POST /api/portfolios
# ---------------------------------------------------------------------------

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    body: PortfolioCreate,
    user: UserInfo = Depends(get_current_user),
) -> PortfolioResponse:
    """Save a newly generated portfolio for the authenticated user."""

    sb = _get_supabase()
    
    # Map the incoming data strictly to the SQL columns
    row = {
        "user_id": user.id,
        "title": body.title,
        "prompt": body.prompt,
        "resume_data": body.resume_data,
        "files": body.files,
        "job_id": body.job_id,
    }

    try:
        result = sb.table("portfolios").insert(row).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database returned empty result after insert.",
            )

        saved = result.data[0]
        return _row_to_response(saved)
        
    except Exception as e:
        logger.error(f"Error creating portfolio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save portfolio: {str(e)}"
        )


# ---------------------------------------------------------------------------
# GET /api/portfolios
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[PortfolioResponse])
async def list_portfolios(
    user: UserInfo = Depends(get_current_user),
) -> list[PortfolioResponse]:
    """Return all portfolios belonging to the authenticated user."""

    sb = _get_supabase()
    
    try:
        result = (
            sb.table("portfolios")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )
        return [_row_to_response(row) for row in (result.data or [])]
        
    except Exception as e:
        logger.error(f"Error fetching portfolios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolios: {str(e)}"
        )


# ---------------------------------------------------------------------------
# GET /api/portfolios/{portfolio_id}
# ---------------------------------------------------------------------------

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: str,
    user: UserInfo = Depends(get_current_user),
) -> PortfolioResponse:
    """Return a single portfolio if it belongs to the authenticated user."""

    sb = _get_supabase()
    
    try:
        result = (
            sb.table("portfolios")
            .select("*")
            .eq("id", portfolio_id)
            .eq("user_id", user.id)
            .maybe_single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found",
            )

        return _row_to_response(result.data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio: {str(e)}"
        )


# ---------------------------------------------------------------------------
# PUT /api/portfolios/{portfolio_id}
# ---------------------------------------------------------------------------

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    body: PortfolioUpdate,
    user: UserInfo = Depends(get_current_user),
) -> PortfolioResponse:
    """Update an existing portfolio's title and/or files."""

    sb = _get_supabase()

    updates: dict[str, Any] = {}
    if body.title is not None:
        updates["title"] = body.title
    if body.files is not None:
        updates["files"] = body.files

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        result = (
            sb.table("portfolios")
            .update(updates)
            .eq("id", portfolio_id)
            .eq("user_id", user.id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found or not owned by you",
            )

        return _row_to_response(result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating portfolio {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update portfolio: {str(e)}"
        )


# ---------------------------------------------------------------------------
# DELETE /api/portfolios/{portfolio_id}
# ---------------------------------------------------------------------------

@router.delete("/{portfolio_id}", status_code=status.HTTP_200_OK)
async def delete_portfolio(
    portfolio_id: str,
    user: UserInfo = Depends(get_current_user),
) -> dict:
    """Delete a portfolio belonging to the authenticated user."""

    sb = _get_supabase()
    
    try:
        result = (
            sb.table("portfolios")
            .delete()
            .eq("id", portfolio_id)
            .eq("user_id", user.id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found or not owned by you",
            )
            
        # Successfully returning a standard dictionary message for the 200 OK status
        return {"message": "Portfolio deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting portfolio {portfolio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete portfolio: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_response(row: dict) -> PortfolioResponse:
    """
    Safely converts a Supabase SQL row dictionary into the Pydantic Response model.
    Uses .get() for nullable fields to prevent KeyError crashes.
    """
    return PortfolioResponse(
        id=row["id"],
        user_id=row["user_id"],
        title=row.get("title") or "My Portfolio",
        prompt=row.get("prompt"),
        resume_data=row.get("resume_data"),
        files=row.get("files") or {},
        job_id=row.get("job_id"),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )