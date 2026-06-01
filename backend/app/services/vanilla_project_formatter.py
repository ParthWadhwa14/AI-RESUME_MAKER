"""
Formatter and normalizer for the generated Vanilla Web project payload.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class VanillaProjectFormatter:
    """
    Cleans up, normalizes, and injects defaults into the raw dict
    produced by the Vanilla Web AI agents.
    """

    @staticmethod
    def _load_scaffold() -> dict[str, str]:
        """Load the provided `vanilla_template.json` scaffold used by the crew."""
        try:
            template_path = (
                Path(__file__).resolve().parents[2]
                / "website_maker"
                / "src"
                / "website_maker"
                / "config"
                / "vanilla_template.json"
            )
            if template_path.is_file():
                with open(template_path, "r", encoding="utf-8") as f:
                    scaffold = json.load(f)
                    if isinstance(scaffold, dict):
                        return scaffold
        except Exception as exc:
            logger.warning("Could not load vanilla_template.json scaffold: %s", exc)
        return {}

    @staticmethod
    def _strip_common_llm_wrappers(text: str) -> str:
        """Best-effort cleanup for common model wrappers around JSON."""
        if not isinstance(text, str):
            return str(text)
        s = text.strip()
        if s.startswith("```"):
            lines = s.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            s = "\n".join(lines).strip()
        if "{" in s and "}" in s:
            start = s.find("{")
            end = s.rfind("}")
            if start >= 0 and end > start:
                s = s[start : end + 1]
        return s.strip()

    @staticmethod
    def _ensure_index_html_valid(out: dict[str, str]) -> None:
        """Ensure index.html is basic and valid HTML5."""
        html = out.get("index.html")
        if not html or "<html" not in html:
            # Revert to scaffold if entirely missing
            scaffold = VanillaProjectFormatter._load_scaffold()
            if scaffold.get("index.html"):
                out["index.html"] = scaffold["index.html"]
                return

    @staticmethod
    def normalize(files: dict[str, Any] | None) -> dict[str, str]:
        """
        Merge the AI-generated payload with the safe fallback scaffold.
        """
        files = files or {}

        # 1. Strip code fences from JSON strings
        clean_files: dict[str, str] = {}
        for filename, content in files.items():
            if not isinstance(content, str):
                continue
            fname = str(filename).strip()
            # If AI wrapped HTML/CSS/JS in markdown fences, strip them
            if content.startswith("```"):
                lines = content.splitlines()
                if lines:
                    lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                clean_files[fname] = "\n".join(lines).strip() + "\n"
            else:
                clean_files[fname] = content

        # 2. Merge with scaffold
        scaffold = VanillaProjectFormatter._load_scaffold()
        out: dict[str, str] = {}

        # Base layer: scaffold files
        for f, content in scaffold.items():
            out[f] = content

        # Override with generated files
        for f, content in clean_files.items():
            # If the AI put files in subdirectories incorrectly, hoist them or just accept them.
            # In vanilla, we just want index.html, style.css, script.js.
            if f.endswith("index.html"):
                out["index.html"] = content
            elif f.endswith("style.css") or f.endswith("styles.css"):
                out["style.css"] = content
            elif f.endswith("script.js") or f.endswith("main.js"):
                out["script.js"] = content
            else:
                # Accept other files (like images or data) if they made any
                out[f] = content

        # Hardening steps
        VanillaProjectFormatter._ensure_index_html_valid(out)

        # Fallback empty files if missing completely
        out.setdefault("style.css", "body { margin: 0; padding: 20px; font-family: sans-serif; }\n")
        out.setdefault("script.js", "console.log('App loaded');\n")

        return out
