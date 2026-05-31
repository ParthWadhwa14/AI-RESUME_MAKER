"""Local portfolio persistence routes.

These routes provide a Supabase-free persistence option for development.
They store generated websites under `backend/local_portfolios/`.

API:
- POST   /api/local-portfolios
- GET    /api/local-portfolios
- GET    /api/local-portfolios/{id}
- DELETE /api/local-portfolios/{id}

No authentication.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.services.local_store.store import LocalPortfolioStore

router = APIRouter(prefix="/api/local-portfolios", tags=["local-portfolios"])

store = LocalPortfolioStore()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_local_portfolio(body: dict):
    try:
        meta = store.create(
            title=body.get("title") or "Untitled Portfolio",
            prompt=body.get("prompt"),
            resume_data=body.get("resume_data"),
            files=body.get("files") or {},
            job_id=body.get("job_id"),
        )
        return {**meta.__dict__}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to save locally: {exc}",
        ) from exc


@router.get("/")
async def list_local_portfolios():
    return [m.__dict__ for m in store.list()]


@router.get("/{portfolio_id}")
async def get_local_portfolio(portfolio_id: str):
    try:
        meta = store.get_meta(portfolio_id)
        files = store.get_files(portfolio_id)
        resume_data = store.get_resume_data(portfolio_id)
        return {
            **meta.__dict__,
            "files": files,
            "resume_data": resume_data,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio not found")


@router.delete("/{portfolio_id}")
async def delete_local_portfolio(portfolio_id: str):
    try:
        store.delete(portfolio_id)
        return {"message": "Deleted"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio not found")


@router.post("/{portfolio_id}/preview")
async def start_portfolio_preview(portfolio_id: str):
    """Start a Vite dev server for a saved local portfolio."""
    from app.services.dev_server_manager import DevServerManager

    try:
        # Verify portfolio exists
        store.get_meta(portfolio_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    project_dir = store._portfolio_dir(portfolio_id) / "files"
    if not project_dir.is_dir():
        raise HTTPException(status_code=404, detail="Portfolio files not found on disk")

    try:
        manager = DevServerManager.instance()
        url = await manager.start_server(
            job_id=portfolio_id,
            project_dir=project_dir,
        )
        return {"preview_url": url, "portfolio_id": portfolio_id}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start preview: {exc}",
        )


@router.delete("/{portfolio_id}/preview")
async def stop_portfolio_preview(portfolio_id: str):
    """Stop the dev server for a saved local portfolio."""
    from app.services.dev_server_manager import DevServerManager

    manager = DevServerManager.instance()
    await manager.stop_server(portfolio_id)
    return {"message": "Preview stopped"}

