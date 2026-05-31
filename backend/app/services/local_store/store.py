from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "untitled"


def _default_base_dir() -> Path:
    # Back-end root (backend/app/services/local_store/store.py -> backend)
    backend_dir = Path(__file__).resolve().parents[3]
    return backend_dir / "local_portfolios"


@dataclass(frozen=True)
class LocalPortfolioMeta:
    id: str
    title: str
    prompt: str | None
    job_id: str | None
    created_at: str
    updated_at: str


class LocalPortfolioStore:
    """Store generated projects on disk.

    Layout:
      backend/local_portfolios/<id>-<slug>/
        meta.json
        resume_data.json
        files/<generated files...>
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or _default_base_dir()).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _portfolio_dir(self, portfolio_id: str, title: str | None = None) -> Path:
        if title:
            return self.base_dir / f"{portfolio_id}-{_slugify(title)}"
        # Fallback: find by prefix
        matches = sorted(self.base_dir.glob(f"{portfolio_id}-*"))
        if matches:
            return matches[0]
        return self.base_dir / portfolio_id

    def create(
        self,
        *,
        title: str,
        prompt: str | None,
        resume_data: dict[str, Any] | None,
        files: dict[str, str],
        job_id: str | None,
    ) -> LocalPortfolioMeta:
        portfolio_id = str(uuid4())
        now = _utc_now_iso()

        pdir = self._portfolio_dir(portfolio_id, title)
        files_dir = pdir / "files"
        files_dir.mkdir(parents=True, exist_ok=True)

        # Write generated files
        for rel_path, code in (files or {}).items():
            rel_path = str(rel_path).lstrip("/")
            out_path = files_dir / rel_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(str(code), encoding="utf-8")

        (pdir / "resume_data.json").write_text(
            json.dumps(resume_data or {}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        meta = {
            "id": portfolio_id,
            "title": title,
            "prompt": prompt,
            "job_id": job_id,
            "created_at": now,
            "updated_at": now,
        }
        (pdir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return LocalPortfolioMeta(**meta)

    def list(self) -> list[LocalPortfolioMeta]:
        items: list[LocalPortfolioMeta] = []
        for meta_file in self.base_dir.glob("*/meta.json"):
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                items.append(LocalPortfolioMeta(**meta))
            except Exception:
                continue
        items.sort(key=lambda m: m.created_at, reverse=True)
        return items

    def get_files(self, portfolio_id: str) -> dict[str, str]:
        pdir = self._portfolio_dir(portfolio_id)
        files_dir = pdir / "files"
        if not files_dir.exists():
            raise FileNotFoundError(portfolio_id)

        out: dict[str, str] = {}
        for path in files_dir.rglob("*"):
            if path.is_file():
                rel = "/" + str(path.relative_to(files_dir)).replace("\\", "/")
                out[rel] = path.read_text(encoding="utf-8")
        return out

    def get_resume_data(self, portfolio_id: str) -> dict[str, Any]:
        pdir = self._portfolio_dir(portfolio_id)
        f = pdir / "resume_data.json"
        if not f.exists():
            return {}
        return json.loads(f.read_text(encoding="utf-8"))

    def get_meta(self, portfolio_id: str) -> LocalPortfolioMeta:
        pdir = self._portfolio_dir(portfolio_id)
        f = pdir / "meta.json"
        if not f.exists():
            raise FileNotFoundError(portfolio_id)
        meta = json.loads(f.read_text(encoding="utf-8"))
        return LocalPortfolioMeta(**meta)

    def delete(self, portfolio_id: str) -> None:
        pdir = self._portfolio_dir(portfolio_id)
        if not pdir.exists():
            raise FileNotFoundError(portfolio_id)
        # Danger but acceptable in dev: recursive delete
        for child in sorted(pdir.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink(missing_ok=True)
            else:
                try:
                    child.rmdir()
                except OSError:
                    pass
        try:
            pdir.rmdir()
        except OSError:
            pass
