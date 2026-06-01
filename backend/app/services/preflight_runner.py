"""
Preflight runner for Vanilla Web projects.
Validates the generated HTML, CSS, and JS before starting the preview.
"""

from __future__ import annotations

import logging
from typing import Any
import re
from dataclasses import dataclass

from app.services.vanilla_project_formatter import VanillaProjectFormatter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreflightIssue:
    """Represents a single validation or build issue."""
    code: str
    message: str


class PreflightError(RuntimeError):
    """Raised when preflight validation fails."""

    def __init__(
        self,
        message: str,
        issues: list[PreflightIssue],
        files: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.issues = issues
        self.files = files


class PreflightRunner:
    """
    Validates Vanilla Web projects (index.html, style.css, script.js).
    """
    
    _REQUIRED_FILES = {"index.html", "style.css", "script.js"}

    @staticmethod
    def _static_validate(files: dict[str, str]) -> list[PreflightIssue]:
        issues: list[PreflightIssue] = []

        for req in PreflightRunner._REQUIRED_FILES:
            if req not in files:
                issues.append(PreflightIssue("missing_required_file", f"Missing required file: {req}"))

        # Basic HTML checks
        html = files.get("index.html", "")
        if html:
            if "<html" not in html or "</html>" not in html:
                issues.append(PreflightIssue("index_html_invalid", "index.html is missing <html> or </html>"))
            
            # Check for unclosed void tags which might break simple parsers
            for line in html.splitlines():
                line_s = line.strip()
                if line_s.startswith("<meta") or line_s.startswith("<link") or line_s.startswith("<img"):
                    if (">" not in line_s) and ("/>" not in line_s):
                        issues.append(PreflightIssue("unclosed_void_tag", f"Unclosed void tag in index.html: {line_s}"))

            # Ensure css and js are linked
            if "style.css" not in html:
                issues.append(PreflightIssue("missing_css_link", "index.html does not link to style.css"))
            if "script.js" not in html:
                issues.append(PreflightIssue("missing_js_link", "index.html does not link to script.js"))

        return issues

    @staticmethod
    async def run_preflight(
        *,
        files: dict[str, Any] | None,
        job_id: str,
    ) -> dict[str, str]:
        # Normalize files
        normalized = VanillaProjectFormatter.normalize(files)

        # Static validation
        static_issues = PreflightRunner._static_validate(normalized)
        if static_issues:
            raise PreflightError("Static validation failed", issues=static_issues, files=normalized)

        # In Vanilla projects, we don't need npm install or build.
        # Just return the normalized files if static validation passes.
        return normalized
