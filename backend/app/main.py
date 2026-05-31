"""
Resume Gala — FastAPI application entry point.

Configures CORS, loads environment variables from the CrewAI ``.env``,
registers route modules, and exposes health / info endpoints.
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add backend directory to sys.path so 'app' is resolvable
_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# 1. MOVE dotenv IMPORTS TO THE VERY TOP
# 1. MOVE dotenv IMPORTS TO THE VERY TOP
from dotenv import load_dotenv

# 2. LOAD ENVIRONMENT VARIABLES IMMEDIATELY
_ENV_PATH = Path(__file__).resolve().parents[1] / "website_maker" / ".env"
if _ENV_PATH.is_file():
    load_dotenv(_ENV_PATH, override=False)
    print(f"Loaded environment from {_ENV_PATH}") 
else:
    print(f"WARNING: .env file not found at {_ENV_PATH}")

# ✅ Corrected: lowercase 'f' in fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 3. NOW WE IMPORT ROUTES
from app.routes import auth, edit, generate, portfolio, resume
from app.routes import local_portfolio

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lifespan: (Now just used for simple startup/shutdown logs)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — runs on startup and shutdown."""
    logger.info("Resume Gala API starting up ✨")
    yield
    # Cleanup all preview dev servers
    try:
        from app.services.dev_server_manager import DevServerManager
        await DevServerManager.instance().cleanup_all()
    except Exception as exc:
        logger.warning("Error cleaning up preview servers: %s", exc)
    logger.info("Resume Gala API shutting down 👋")

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Resume Gala API",
    description="AI-powered portfolio website generator backend",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js frontend during development
# ---------------------------------------------------------------------------

_ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allow overriding via env var for production deployments
_extra = os.getenv("CORS_ORIGINS", "")
if _extra:
    _ALLOWED_ORIGINS.extend(origin.strip() for origin in _extra.split(",") if origin.strip())

# Allow preview dev server ports (5200–5220)
for _port in range(5200, 5221):
    _ALLOWED_ORIGINS.append(f"http://localhost:{_port}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(generate.router)
app.include_router(edit.router)
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(portfolio.router)
app.include_router(local_portfolio.router)


# ---------------------------------------------------------------------------
# Root / health endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["meta"])
async def root():
    """Return basic API information."""
    return {
        "name": "Resume Gala API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["meta"])
async def health_check():
    """Lightweight health-check endpoint for load balancers / uptime monitors."""
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# Preview management
# ---------------------------------------------------------------------------

@app.get("/api/preview/{job_id}", tags=["preview"])
async def get_preview_url(job_id: str):
    """Return the live dev-server URL for a generated portfolio."""
    from app.services.dev_server_manager import DevServerManager

    manager = DevServerManager.instance()
    url = manager.get_server_url(job_id)
    if url is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No preview server running for this job")
    return {"preview_url": url, "job_id": job_id}


@app.delete("/api/preview/{job_id}", tags=["preview"])
async def stop_preview(job_id: str):
    """Stop the dev server for a generated portfolio."""
    from app.services.dev_server_manager import DevServerManager

    manager = DevServerManager.instance()
    await manager.stop_server(job_id)
    return {"message": f"Preview server for job {job_id} stopped"}


@app.get("/api/previews", tags=["preview"])
async def list_previews():
    """List all running preview servers (for debugging)."""
    from app.services.dev_server_manager import DevServerManager

    manager = DevServerManager.instance()
    return {"servers": manager.get_all_servers()}