#!/usr/bin/env python
"""
Resume Gala — Project Entry Point
Start the FastAPI backend server.
"""
import uvicorn


def main():
    """Launch the Resume Gala backend API server."""
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
    )


if __name__ == "__main__":
    main()
