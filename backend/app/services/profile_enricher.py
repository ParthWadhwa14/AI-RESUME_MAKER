"""
Profile enrichment service for GitHub + LinkedIn URLs.

This service augments resume_input with public profile information before
running CrewAI generation.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class ProfileEnricher:
    """Fetches and merges public profile data into resume input."""

    @staticmethod
    def _extract_github_username(github_url: str) -> str | None:
        try:
            parsed = urlparse(github_url)
            if "github.com" not in parsed.netloc.lower():
                return None
            path = parsed.path.strip("/")
            if not path:
                return None
            return path.split("/")[0]
        except Exception:
            return None

    @staticmethod
    async def _fetch_github_profile(github_url: str) -> dict:
        username = ProfileEnricher._extract_github_username(github_url)
        if not username:
            return {"error": "Invalid GitHub URL"}

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "resume-gala-enricher",
        }
        base = "https://api.github.com"

        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            user_resp = await client.get(f"{base}/users/{username}")
            user_resp.raise_for_status()
            user = user_resp.json()

            repos_resp = await client.get(
                f"{base}/users/{username}/repos",
                params={"per_page": 100, "sort": "updated"},
            )
            repos_resp.raise_for_status()
            repos = repos_resp.json()

        repo_data = []
        for repo in repos:
            repo_data.append(
                {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "url": repo.get("html_url"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "topics": repo.get("topics", []),
                    "homepage": repo.get("homepage"),
                }
            )

        return {
            "username": user.get("login"),
            "name": user.get("name"),
            "bio": user.get("bio"),
            "company": user.get("company"),
            "location": user.get("location"),
            "blog": user.get("blog"),
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "public_repos": user.get("public_repos", 0),
            "profile_url": user.get("html_url"),
            "repos": repo_data,
        }

    @staticmethod
    async def _fetch_linkedin_profile(linkedin_url: str) -> dict:
        # LinkedIn heavily restricts scraping; this is best-effort extraction
        # from public metadata only.
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                resp = await client.get(linkedin_url)
                resp.raise_for_status()
                html = resp.text

            title = None
            description = None
            if "<title>" in html and "</title>" in html:
                title = html.split("<title>", 1)[1].split("</title>", 1)[0].strip()

            marker = 'property="og:description" content="'
            if marker in html:
                description = html.split(marker, 1)[1].split('"', 1)[0].strip()

            return {
                "profile_url": linkedin_url,
                "title": title,
                "summary": description,
                "note": "Public metadata only. Full LinkedIn data may require official API or manual input.",
            }
        except Exception as exc:
            return {
                "profile_url": linkedin_url,
                "error": str(exc),
                "note": "Could not fetch LinkedIn profile metadata.",
            }

    @staticmethod
    async def enrich(
        resume_input: dict,
        github_url: str | None = None,
        linkedin_url: str | None = None,
    ) -> dict:
        enriched = dict(resume_input or {})
        personal = enriched.get("personal")
        if not isinstance(personal, dict):
            personal = {}
        social = personal.get("social")
        if not isinstance(social, dict):
            social = {}

        if github_url:
            social["github"] = github_url
        if linkedin_url:
            social["linkedin"] = linkedin_url
        personal["social"] = social
        enriched["personal"] = personal

        enrichment = {}

        if github_url:
            try:
                enrichment["github"] = await ProfileEnricher._fetch_github_profile(github_url)
            except Exception as exc:
                logger.warning("GitHub enrichment failed: %s", exc)
                enrichment["github"] = {"error": str(exc), "profile_url": github_url}

        if linkedin_url:
            enrichment["linkedin"] = await ProfileEnricher._fetch_linkedin_profile(linkedin_url)

        if enrichment:
            enriched["_profile_enrichment"] = enrichment

        # Ensure compatibility with prompts expecting top-level keys.
        if not enriched.get("name"):
            enriched["name"] = personal.get("name", "")
        if not enriched.get("title"):
            enriched["title"] = personal.get("title", "")
        if github_url and not enriched.get("github_url"):
            enriched["github_url"] = github_url
        if linkedin_url and not enriched.get("linkedin_url"):
            enriched["linkedin_url"] = linkedin_url

        return enriched
