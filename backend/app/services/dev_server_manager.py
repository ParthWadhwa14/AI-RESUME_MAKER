"""
DevServerManager — Manages live Vite dev servers for generated portfolios.

Spins up `npm run dev` on a unique port for each portfolio so the user
can preview the full-fidelity site (with Tailwind, Framer Motion, etc.)
instead of relying on the limited Sandpack in-browser sandbox.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import shutil
import signal
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Port range for preview dev servers
_PORT_RANGE_START = 5200
_PORT_RANGE_END = 5220  # max 20 concurrent previews

# How long (seconds) before a server is considered stale and auto-stopped
_AUTO_STOP_TIMEOUT_SECONDS = int(os.getenv("PREVIEW_AUTO_STOP_SECONDS", "1800"))  # 30 min

# Max time to wait for npm install
_NPM_INSTALL_TIMEOUT = int(os.getenv("PREVIEW_NPM_INSTALL_TIMEOUT", "180"))  # 3 min

# Max time to wait for the dev server to become responsive
_SERVER_READY_TIMEOUT = int(os.getenv("PREVIEW_SERVER_READY_TIMEOUT", "30"))  # 30 sec


@dataclass
class _ServerEntry:
    """Tracks a running preview server (Vite or plain static)."""
    job_id: str
    port: int
    process: asyncio.subprocess.Process
    project_dir: Path
    started_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

    @property
    def url(self) -> str:
        # Use explicit IPv4 loopback to avoid localhost -> ::1 resolution mismatches
        # that can lead to "refused to connect" in browsers/iframes on some macOS setups.
        return f"http://127.0.0.1:{self.port}"

    @property
    def is_stale(self) -> bool:
        return (time.time() - self.last_accessed) > _AUTO_STOP_TIMEOUT_SECONDS


class DevServerManager:
    """Singleton-ish manager for live preview dev servers.

    Usage::

        manager = DevServerManager.instance()
        url = await manager.start_server(job_id, project_dir)
        # ... later ...
        await manager.stop_server(job_id)
    """

    _instance: Optional["DevServerManager"] = None

    def __init__(self) -> None:
        self._servers: dict[str, _ServerEntry] = {}
        self._used_ports: set[int] = set()
        self._lock = asyncio.Lock()

    @classmethod
    def instance(cls) -> "DevServerManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _allocate_port(self) -> int:
        """Find the next available port in the range."""
        for port in range(_PORT_RANGE_START, _PORT_RANGE_END + 1):
            if port not in self._used_ports:
                self._used_ports.add(port)
                return port
        raise RuntimeError(
            f"No available ports in range {_PORT_RANGE_START}-{_PORT_RANGE_END}. "
            f"Stop some preview servers first."
        )

    def _release_port(self, port: int) -> None:
        self._used_ports.discard(port)

    @staticmethod
    async def _run_npm_install(project_dir: Path) -> None:
        """Run npm install in the project directory."""
        npm = shutil.which("npm")
        if not npm:
            raise RuntimeError("npm not found on PATH")

        logger.info("Running npm install in %s …", project_dir)
        proc = await asyncio.create_subprocess_exec(
            npm, "install",
            cwd=str(project_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={
                **os.environ,
                "NPM_CONFIG_FUND": "false",
                "NPM_CONFIG_AUDIT": "false",
                "NPM_CONFIG_UPDATE_NOTIFIER": "false",
            },
        )

        try:
            out_b, _ = await asyncio.wait_for(
                proc.communicate(), timeout=_NPM_INSTALL_TIMEOUT
            )
        except asyncio.TimeoutError:
            with contextlib.suppress(ProcessLookupError):
                proc.kill()
            raise RuntimeError(
                f"npm install timed out after {_NPM_INSTALL_TIMEOUT}s"
            )

        out = (out_b or b"").decode("utf-8", errors="replace")
        if proc.returncode != 0:
            raise RuntimeError(f"npm install failed (rc={proc.returncode}):\n{out[-3000:]}")

        logger.info("npm install completed successfully in %s", project_dir)

    @staticmethod
    async def _wait_for_http_200(url: str, timeout: int) -> bool:
        """Poll until an HTTP server responds (stdlib-only)."""
        import urllib.request
        import urllib.error

        deadline = time.time() + timeout

        def _probe() -> bool:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:  # nosec - local dev URL
                    status = getattr(resp, "status", 200)
                    return int(status) < 500
            except (urllib.error.URLError, ValueError):
                return False

        while time.time() < deadline:
            ok = await asyncio.to_thread(_probe)
            if ok:
                return True
            await asyncio.sleep(0.5)
        return False

    @staticmethod
    def _is_vite_project(project_dir: Path) -> bool:
        """Return True if this folder looks like a Vite project."""
        pkg = project_dir / "package.json"
        # If there's no package.json, it is definitely not a Vite project.
        if not pkg.is_file():
            return False
        # If index.html exists, that's a strong Vite signal.
        if (project_dir / "index.html").is_file():
            return True
        # Be conservative: require a Vite config OR src/main.* entry.
        if (project_dir / "vite.config.js").is_file() or (project_dir / "vite.config.ts").is_file():
            return True
        if (project_dir / "src" / "main.jsx").is_file() or (project_dir / "src" / "main.tsx").is_file() or (project_dir / "src" / "main.js").is_file() or (project_dir / "src" / "main.ts").is_file():
            return True
        return False

    @staticmethod
    def _has_root_index_html(project_dir: Path) -> bool:
        return (project_dir / "index.html").is_file()

    async def start_server(
        self,
        job_id: str,
        project_dir: Path,
        *,
        skip_install: bool = False,
    ) -> str:
        """Start a preview server for the given project.

        - If `project_dir` looks like a Vite project, start Vite.
        - Otherwise, if it contains a root `index.html`, start a simple static server.

        This avoids trying to launch Vite for plain HTML/CSS/JS outputs.
        """
        async with self._lock:
            # If a server is already running for this job, return its URL
            existing = self._servers.get(job_id)
            if existing is not None:
                existing.last_accessed = time.time()
                logger.info("Dev server already running for job %s at %s", job_id, existing.url)
                return existing.url

            port = self._allocate_port()

        try:
            # Decide server type
            is_vite = self._is_vite_project(project_dir)
            has_index = self._has_root_index_html(project_dir)

            if not is_vite:
                # Plain static site: require index.html
                if not has_index:
                    raise RuntimeError(
                        "Preview project is not a Vite project and no root index.html was found. "
                        "Generate either a Vite scaffold (package.json + index.html) or a plain static site (index.html)."
                    )

                python = shutil.which("python3") or shutil.which("python")
                if not python:
                    raise RuntimeError("python3 not found on PATH")

                logger.info("Starting static http.server for job %s on port %d …", job_id, port)

                proc = await asyncio.create_subprocess_exec(
                    python,
                    "-m",
                    "http.server",
                    str(port),
                    "--bind",
                    "127.0.0.1",
                    cwd=str(project_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    env={
                        **os.environ,
                        "PYTHONUNBUFFERED": "1",
                    },
                )

                entry = _ServerEntry(job_id=job_id, port=port, process=proc, project_dir=project_dir)

                # Wait for readiness (root page)
                ready = await self._wait_for_http_200(entry.url, _SERVER_READY_TIMEOUT)
                if not ready and proc.returncode is not None:
                    out_b = await proc.stdout.read() if proc.stdout else b""
                    out = out_b.decode("utf-8", errors="replace")
                    self._release_port(port)
                    raise RuntimeError(
                        f"static http.server exited immediately (rc={proc.returncode}):\n{out[-2000:]}"
                    )

                async with self._lock:
                    self._servers[job_id] = entry

                logger.info("Static preview server for job %s is live at %s", job_id, entry.url)
                return entry.url

            # Vite project
            if not skip_install:
                await self._run_npm_install(project_dir)

            npm = shutil.which("npm")
            if not npm:
                raise RuntimeError("npm not found on PATH")

            npx = shutil.which("npx")
            if not npx:
                npx = npm.replace("npm", "npx")

            logger.info("Starting Vite dev server for job %s on port %d …", job_id, port)

            proc = await asyncio.create_subprocess_exec(
                npx,
                "vite",
                "--port",
                str(port),
                "--host",
                "127.0.0.1",
                "--strictPort",
                cwd=str(project_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={
                    **os.environ,
                    "NODE_ENV": "development",
                    "BROWSER": "none",
                },
            )

            entry = _ServerEntry(job_id=job_id, port=port, process=proc, project_dir=project_dir)

            ready = await self._wait_for_http_200(entry.url, _SERVER_READY_TIMEOUT)
            if not ready:
                if proc.returncode is not None:
                    out_b = await proc.stdout.read() if proc.stdout else b""
                    out = out_b.decode("utf-8", errors="replace")
                    self._release_port(port)
                    raise RuntimeError(
                        f"Vite dev server exited immediately (rc={proc.returncode}):\n{out[-2000:]}"
                    )
                logger.warning(
                    "Dev server for job %s on port %d did not respond within %ds, "
                    "but process is still running — continuing anyway.",
                    job_id,
                    port,
                    _SERVER_READY_TIMEOUT,
                )

            async with self._lock:
                self._servers[job_id] = entry

            logger.info("Dev server for job %s is live at %s", job_id, entry.url)
            return entry.url

        except Exception:
            self._release_port(port)
            raise

    async def stop_server(self, job_id: str) -> None:
        """Stop the dev server for the given job, if running."""
        async with self._lock:
            entry = self._servers.pop(job_id, None)

        if entry is None:
            return

        logger.info("Stopping dev server for job %s (port %d) …", job_id, entry.port)
        try:
            if entry.process.returncode is None:
                # Send SIGTERM first, then SIGKILL after a short wait
                try:
                    entry.process.send_signal(signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    await asyncio.wait_for(entry.process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    with contextlib.suppress(ProcessLookupError):
                        entry.process.kill()
                    await asyncio.sleep(0.5)
        except Exception as exc:
            logger.warning("Error stopping dev server for job %s: %s", job_id, exc)
        finally:
            self._release_port(entry.port)

    def get_server_url(self, job_id: str) -> str | None:
        """Return the URL of the dev server for the given job, or None."""
        entry = self._servers.get(job_id)
        if entry is None:
            return None
        entry.last_accessed = time.time()
        return entry.url

    def get_all_servers(self) -> list[dict]:
        """Return info about all running servers (for debugging)."""
        return [
            {
                "job_id": e.job_id,
                "port": e.port,
                "url": e.url,
                "project_dir": str(e.project_dir),
                "started_at": e.started_at,
                "last_accessed": e.last_accessed,
                "is_stale": e.is_stale,
                "pid": e.process.pid,
            }
            for e in self._servers.values()
        ]

    async def cleanup_stale(self) -> int:
        """Stop all stale servers. Returns the number stopped."""
        stale_ids = [
            job_id
            for job_id, entry in self._servers.items()
            if entry.is_stale
        ]
        for job_id in stale_ids:
            await self.stop_server(job_id)
        if stale_ids:
            logger.info("Cleaned up %d stale preview server(s)", len(stale_ids))
        return len(stale_ids)

    async def cleanup_all(self) -> None:
        """Stop all running servers (call on app shutdown)."""
        job_ids = list(self._servers.keys())
        for job_id in job_ids:
            await self.stop_server(job_id)
        logger.info("All preview servers stopped (%d total)", len(job_ids))
