"""
Resume parsing utilities for JSON, TXT, and PDF uploads.
"""

from __future__ import annotations

import io
import json
import re
from typing import Any

from pypdf import PdfReader


_HEADING_ALIASES = {
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
    ],
    "education": [
        "education",
        "academic background",
        "academics",
    ],
    "projects": [
        "projects",
        "project",
    ],
    "skills": [
        "skills",
        "technical skills",
        "technologies",
        "tech stack",
    ],
}

_DATE_PATTERN = re.compile(
    r"(?:\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b|\b\d{4}\b\s*[-–to]+\s*(?:\d{4}|present)|\bpresent\b)",
    re.IGNORECASE,
)

_ROLE_HINTS = {
    "intern",
    "engineer",
    "developer",
    "analyst",
    "consultant",
    "manager",
    "designer",
    "research",
    "lead",
}


def _clean_line(line: str) -> str:
    line = line.replace("\u2013", "-").replace("\u2014", "-")
    line = line.replace("\u00a0", " ")
    # Fix common PDF extraction artifacts: "F umind" -> "Fumind", "T echnology" -> "Technology"
    line = re.sub(r"\b([A-Za-z])\s+([a-z]{2,})\b", r"\1\2", line)
    line = re.sub(r"\s+", " ", line.strip())
    return line


def _is_heading(line: str) -> tuple[bool, str | None]:
    normalized = re.sub(r"[^a-z0-9 ]+", "", line.lower()).strip()
    for canonical, aliases in _HEADING_ALIASES.items():
        if normalized in aliases:
            return True, canonical
    return False, None


def _split_into_blocks(section_text: str) -> list[list[str]]:
    lines = [_clean_line(line) for line in section_text.splitlines()]
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if not line:
            if current:
                blocks.append(current)
                current = []
            continue
        # Start a new block when a likely new entry header appears.
        if (
            current
            and (
                " at " in line.lower()
                or "|" in line
                or re.search(r"\b(intern|engineer|developer|analyst|manager)\b", line, re.IGNORECASE)
            )
            and len(line) > 16
            and not line.lstrip().startswith(("-", "*", "•"))
        ):
            blocks.append(current)
            current = [line]
            continue
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _extract_email(text: str) -> str | None:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def _extract_links(text: str) -> dict[str, str]:
    links = {}
    github = re.search(r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+", text, re.IGNORECASE)
    linkedin = re.search(
        r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+",
        text,
        re.IGNORECASE,
    )
    if github:
        links["github"] = github.group(0)
    if linkedin:
        links["linkedin"] = linkedin.group(0)
    return links


def _extract_sections(text: str) -> dict[str, str]:
    lines = text.splitlines()
    markers: list[tuple[str, int]] = []
    for idx, raw_line in enumerate(lines):
        is_heading, canonical = _is_heading(raw_line)
        if is_heading and canonical:
            markers.append((canonical, idx))

    sections: dict[str, str] = {}
    for i, (name, start_idx) in enumerate(markers):
        end_idx = markers[i + 1][1] if i + 1 < len(markers) else len(lines)
        body = "\n".join(lines[start_idx + 1 : end_idx]).strip()
        if body:
            sections[name] = body
    return sections


def _extract_name_title(lines: list[str]) -> tuple[str, str]:
    non_empty = [_clean_line(line) for line in lines if _clean_line(line)]
    if not non_empty:
        return "", ""

    candidates = []
    for line in non_empty[:8]:
        is_heading, _ = _is_heading(line)
        if is_heading:
            break
        if "@" in line or "linkedin.com" in line.lower() or "github.com" in line.lower():
            continue
        candidates.append(line)

    name = candidates[0] if candidates else non_empty[0]
    title = candidates[1] if len(candidates) > 1 else ""
    if len(name.split()) > 8:
        name = non_empty[0]
    # If title is packed with separators, keep only the most role-like slice.
    if "|" in title:
        parts = [p.strip() for p in title.split("|") if p.strip()]
        role_like = next((p for p in parts if any(k in p.lower() for k in _ROLE_HINTS)), "")
        title = role_like or parts[-1]
    return name, title


def _extract_timeline(text: str) -> str:
    matches = _DATE_PATTERN.findall(text)
    if not matches:
        return ""
    return " - ".join(dict.fromkeys(matches))[:80]


def _parse_experience_block(block: list[str]) -> dict[str, Any] | None:
    if not block:
        return None

    header = block[0]
    body_text = " ".join(block)
    timeline = _extract_timeline(body_text)

    role = ""
    company = ""

    if " at " in header.lower():
        left, right = re.split(r"\bat\b", header, maxsplit=1, flags=re.IGNORECASE)
        role, company = left.strip(" -|,"), right.strip(" -|,")
    elif "|" in header:
        left, right = [part.strip() for part in header.split("|", 1)]
        role, company = left, right
    elif " - " in header:
        left, right = [part.strip() for part in header.split(" - ", 1)]
        # Prefer "Role - Company" if role-like tokens exist on left.
        if any(token in left.lower() for token in _ROLE_HINTS):
            role, company = left, right
        else:
            company, role = left, right
    else:
        # Pattern fallback: "AI Intern - Fumind.ai Remote Feb-April 2026"
        if "-" in header:
            parts = [p.strip() for p in header.split("-", 1)]
            if len(parts) == 2 and any(token in parts[0].lower() for token in _ROLE_HINTS):
                role, company = parts[0], parts[1]
            else:
                company = header
        else:
            company = header

    highlights = []
    for line in block[1:]:
        cleaned = line.lstrip("-*• ").strip()
        if not cleaned:
            continue
        if cleaned != header and cleaned not in highlights:
            highlights.append(cleaned)

    if not role and not any(token in header.lower() for token in _ROLE_HINTS):
        # Reject weak noisy lines that are unlikely to be actual jobs.
        return None

    return {
        "company": company[:120],
        "role": role[:120],
        "timeline": timeline,
        "highlights": highlights[:4],
    }


def _parse_education_block(block: list[str]) -> dict[str, Any] | None:
    if not block:
        return None
    header = block[0]
    timeline = _extract_timeline(" ".join(block))
    degree = ""
    if len(block) > 1:
        degree = block[1].lstrip("-*• ").strip()
    return {
        "institution": header[:140],
        "degree": degree[:140],
        "timeline": timeline,
    }


def _parse_project_block(block: list[str]) -> dict[str, Any] | None:
    if not block:
        return None
    title = block[0]
    # Split title if technologies got appended inline.
    if "|" in title:
        title = title.split("|", 1)[0].strip()
    description = " ".join(line.lstrip("-*• ").strip() for line in block[1:]).strip()
    # Guard against merged multiple projects in one paragraph.
    description = re.split(r"\b(?:Project|PROJECT)\b[:\s-]", description, maxsplit=1)[0].strip() or description
    if not description:
        description = title
    return {
        "title": title[:140],
        "description": description[:500],
        "technologies": [],
    }


def _parse_skills(section_text: str) -> list[str]:
    tokens: list[str] = []
    cleaned_section = re.sub(
        r"\b(?:languages?|frameworks?\s*&?\s*libraries?|ai\s*&?\s*llms?|tools?)\s*:\s*",
        "",
        section_text,
        flags=re.IGNORECASE,
    )
    for part in re.split(r"[\n,|•;/]+", cleaned_section):
        cleaned = part.strip(" -\t")
        if not cleaned:
            continue
        if len(cleaned) < 2 or len(cleaned) > 40:
            continue
        lower = cleaned.lower()
        if lower in {"skills", "technical skills", "technologies"}:
            continue
        tokens.append(cleaned)
    return list(dict.fromkeys(tokens))[:30]


def parse_text_resume(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    full_text = "\n".join(_clean_line(line) for line in lines if _clean_line(line))
    links = _extract_links(full_text)
    email = _extract_email(full_text)
    sections = _extract_sections(text)

    name, title = _extract_name_title(lines)

    skills = _parse_skills(sections.get("skills", ""))

    experience: list[dict[str, Any]] = []
    for block in _split_into_blocks(sections.get("experience", "")):
        parsed = _parse_experience_block(block)
        if parsed:
            experience.append(parsed)

    education: list[dict[str, Any]] = []
    for block in _split_into_blocks(sections.get("education", "")):
        parsed = _parse_education_block(block)
        if parsed:
            education.append(parsed)

    projects: list[dict[str, Any]] = []
    for block in _split_into_blocks(sections.get("projects", "")):
        parsed = _parse_project_block(block)
        if parsed:
            projects.append(parsed)

    return {
        "personal": {
            "name": name,
            "title": title,
            "email": email or "",
            "social": {
                "github": links.get("github", ""),
                "linkedin": links.get("linkedin", ""),
            },
        },
        "education": education,
        "experience": experience,
        "skills": skills,
        "projects": projects,
        "additional_context": [],
        "_raw_resume_text": full_text[:20000],
        "_parser_confidence_notes": [
            "Section-block parser applied for experience/education/projects."
        ],
    }


def parse_pdf_resume(content: bytes) -> dict[str, Any]:
    reader = PdfReader(io.BytesIO(content))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return parse_text_resume(text)


def parse_json_resume(text: str) -> dict[str, Any]:
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("JSON resume must be an object")
    return parsed
