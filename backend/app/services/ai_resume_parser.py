"""
AI-agent-based resume parsing service with safe fallback behavior.
"""

from __future__ import annotations

import os
import json
import logging
import re
from typing import Any

# Prevent interactive telemetry/tracing prompts in server mode.
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

from crewai import Agent, Crew, Process, Task

logger = logging.getLogger(__name__)


_PARSER_PROMPT = """
You are an expert resume parsing agent.
Convert the provided raw resume text into STRICT JSON with this schema:
{
  "personal": {
    "name": "string",
    "title": "string",
    "email": "string",
    "social": {"github": "string", "linkedin": "string"}
  },
  "education": [{"institution":"string","degree":"string","timeline":"string"}],
  "experience": [{"company":"string","role":"string","timeline":"string","highlights":["string"]}],
  "skills": ["string"],
  "projects": [{"title":"string","description":"string","technologies":["string"]}]
}

Rules:
- Output ONLY valid JSON, no markdown fences.
- Do not invent details not present in input.
- Keep experience/project entries deduplicated and concise.
- If uncertain, keep fields empty instead of hallucinating.
"""


def _extract_json(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        raise ValueError("No JSON object found in AI parser output")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("AI parser output is not a JSON object")
    return parsed


def parse_resume_with_ai(raw_resume_text: str) -> dict[str, Any]:
    """
    Parse resume text via a dedicated CrewAI single-agent pipeline.
    """
    parser_agent = Agent(
        role="Resume Parsing Specialist",
        goal="Extract structured resume JSON accurately",
        backstory="You convert messy resume text into a clean structured JSON payload.",
        verbose=False,
        max_iter=6,
    )

    parser_task = Task(
        description=(
            f"{_PARSER_PROMPT}\n\nRaw resume text:\n{raw_resume_text[:25000]}"
        ),
        expected_output="Strict JSON object matching the required schema.",
        agent=parser_agent,
    )

    crew = Crew(
        agents=[parser_agent],
        tasks=[parser_task],
        process=Process.sequential,
        verbose=False,
        max_rpm=20,
    )

    result = crew.kickoff()
    raw = result.raw if hasattr(result, "raw") else str(result)
    parsed = _extract_json(raw)
    logger.info("AI resume parser produced structured output.")
    return parsed
