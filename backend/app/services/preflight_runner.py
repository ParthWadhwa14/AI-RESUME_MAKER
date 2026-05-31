from __future__ import annotations

import asyncio
import contextlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.react_project_formatter import ReactProjectFormatter


@dataclass(frozen=True)
class PreflightIssue:
    code: str
    message: str


class PreflightError(RuntimeError):
    def __init__(self, message: str, *, issues: list[PreflightIssue] | None = None) -> None:
        super().__init__(message)
        self.issues = issues or []


class PreflightRunner:
    """Deterministic validations + optional `npm install` + `npm run build`.

    Option 2 implementation:
      - Stage normalized Vite project in a temp folder
      - Run static checks (required files, basic HTML sanity)
      - Run `npm install` and `npm run build` with strict timeouts

    Notes
    -----
    - This runs server-side (FastAPI) and does *not* grant the LLM direct FS/terminal access.
    - It is guarded by env flags + timeouts.
    """

    # Required minimal Vite+React scaffold
    _REQUIRED_FILES = (
        "package.json",
        "index.html",
        "vite.config.js",
        "src/main.jsx",
        "src/App.jsx",
    )

    @staticmethod
    def _backend_dir() -> Path:
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def _staging_root() -> Path:
        backend_dir = PreflightRunner._backend_dir()
        root = backend_dir / "preflight_staging"
        root.mkdir(parents=True, exist_ok=True)
        return root

    @staticmethod
    def _should_run_build() -> bool:
        val = (os.getenv("PREFLIGHT_ENABLE_BUILD", "1") or "").strip().lower()
        return val not in {"0", "false", "no", "off"}

    @staticmethod
    def _timeouts() -> tuple[int, int]:
        install_s = int(os.getenv("PREFLIGHT_NPM_INSTALL_TIMEOUT_SECONDS", "180"))
        build_s = int(os.getenv("PREFLIGHT_NPM_BUILD_TIMEOUT_SECONDS", "120"))
        return install_s, build_s

    @staticmethod
    def _write_files(project_dir: Path, files: dict[str, str]) -> None:
        for rel, content in (files or {}).items():
            rel = str(rel).lstrip("/\\")
            out_path = project_dir / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(str(content), encoding="utf-8")

    @staticmethod
    def _static_validate(files: dict[str, str]) -> list[PreflightIssue]:
        issues: list[PreflightIssue] = []

        for req in PreflightRunner._REQUIRED_FILES:
            if req not in files:
                issues.append(PreflightIssue("missing_required_file", f"Missing required file: {req}"))

        # Basic HTML checks to avoid parse5 crashes (not a full HTML parser)
        html = files.get("index.html", "")
        if html:
            if "<html" not in html or "</html>" not in html:
                issues.append(PreflightIssue("index_html_invalid", "index.html is missing <html> or </html>"))
            # basic unclosed meta/link/img tag detection (common LLM failure)
            for line in html.splitlines():
                line_s = line.strip()
                if line_s.startswith("<meta") or line_s.startswith("<link") or line_s.startswith("<img"):
                    if (">" not in line_s) and ("/>" not in line_s):
                        issues.append(PreflightIssue("index_html_invalid", f"Possibly unclosed tag in index.html: {line_s}"))
                        break

        # Ensure package.json is JSON
        pkg = files.get("package.json", "")
        if pkg:
            try:
                json.loads(pkg)
            except Exception:
                issues.append(PreflightIssue("package_json_invalid", "package.json is not valid JSON"))

        return issues

    @staticmethod
    async def _run_cmd(cmd: list[str], *, cwd: Path, timeout_s: int) -> tuple[int, str]:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={
                **os.environ,
                # reduce noisy downloads a bit
                "NPM_CONFIG_FUND": "false",
                "NPM_CONFIG_AUDIT": "false",
                "NPM_CONFIG_UPDATE_NOTIFIER": "false",
            },
        )

        try:
            out_b, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        except asyncio.TimeoutError:
            with contextlib.suppress(ProcessLookupError):
                proc.kill()
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(proc.communicate(), timeout=2)
            raise

        out = (out_b or b"").decode("utf-8", errors="replace")
        return proc.returncode or 0, out

    @staticmethod
    def _fix_common_icon_imports(files: dict[str, str]) -> tuple[dict[str, str], list[PreflightIssue]]:
        """Repair common icon-import mistakes that crash Vite builds.

        - `AiOutlineLinkedin` is a react-icons symbol, not lucide-react.
        - If react-icons symbols are imported from lucide-react, rewrite to lucide equivalents.
        - If react-icons is imported/used but not declared, add it.
        """
        issues: list[PreflightIssue] = []

        # 1) Fix obvious wrong imports: `{ AiOutlineLinkedin } from 'lucide-react'`
        # Map to lucide names (keep minimal; can be extended).
        lucide_map = {
            "AiOutlineLinkedin": "Linkedin",
            "AiFillLinkedin": "Linkedin",
            "FaLinkedin": "Linkedin",
            "FaLinkedinIn": "Linkedin",
            "AiOutlineGithub": "Github",
            "FaGithub": "Github",
            "AiOutlineMail": "Mail",
            "MdEmail": "Mail",
        }

        pattern = re.compile(r"import\s*\{([^}]+)\}\s*from\s*['\"]lucide-react['\"];?")

        def _rewrite_import_line(line: str) -> str:
            m = pattern.search(line)
            if not m:
                return line
            raw_names = [n.strip() for n in m.group(1).split(",") if n.strip()]
            new_names: list[str] = []
            changed = False
            for n in raw_names:
                if n in lucide_map:
                    new_names.append(lucide_map[n])
                    changed = True
                else:
                    new_names.append(n)
            if changed:
                return line[: m.start()] + f"import {{ {', '.join(new_names)} }} from 'lucide-react';" + line[m.end() :]
            return line

        updated = dict(files)
        for path, content in list(updated.items()):
            if not path.startswith("src/"):
                continue
            if not isinstance(content, str):
                continue
            if "lucide-react" not in content:
                continue
            lines = content.splitlines()
            new_lines = [_rewrite_import_line(l) for l in lines]
            if new_lines != lines:
                updated[path] = "\n".join(new_lines) + ("\n" if content.endswith("\n") else "")
                issues.append(PreflightIssue("fixed_icon_imports", f"Rewrote invalid lucide-react icon imports in {path}"))

        # 2) Ensure react-icons dependency if it's imported.
        uses_react_icons = any("from 'react-icons" in (updated.get(p) or "") for p in updated.keys())
        if uses_react_icons:
            pkg_raw = updated.get("package.json", "")
            try:
                pkg = json.loads(pkg_raw) if pkg_raw else {}
            except Exception:
                pkg = {}
            deps = pkg.get("dependencies", {}) if isinstance(pkg.get("dependencies"), dict) else {}
            if "react-icons" not in deps:
                deps["react-icons"] = "^5.2.1"
                pkg["dependencies"] = deps
                updated["package.json"] = json.dumps(pkg, ensure_ascii=False, indent=2) + "\n"
                issues.append(PreflightIssue("added_dependency", "Added react-icons to package.json"))

        return updated, issues

    @staticmethod
    def _fix_jsx_void_tags(content: str) -> tuple[str, bool]:
        """Self-close common HTML void tags in JSX/TSX content."""
        pattern = re.compile(r'<(img|input|br|hr|link|meta)\b([^>]*)(?<!/)>')
        new_content, count = pattern.subn(r'<\1\2 />', content)
        return new_content, count > 0

    @staticmethod
    def _fix_react_hooks_imports(content: str) -> tuple[str, bool]:
        """Auto-inject missing React hooks imports from 'react'."""
        hooks = ["useState", "useEffect", "useRef", "useMemo", "useCallback"]
        needed_hooks = []
        for hook in hooks:
            if re.search(r'\b' + hook + r'\b', content):
                if re.search(r'\bReact\.' + hook + r'\b', content):
                    continue
                imported = False
                for line in content.splitlines():
                    if "import" in line and "from" in line and ("'react'" in line or '"react"' in line):
                        if hook in line:
                            imported = True
                            break
                if not imported:
                    needed_hooks.append(hook)
        if needed_hooks:
            hooks_str = ", ".join(needed_hooks)
            content = f"import {{ {hooks_str} }} from 'react';\n" + content
            return content, True
        return content, False

    @staticmethod
    def _fix_framer_motion_imports(content: str) -> tuple[str, bool]:
        """Auto-inject Framer Motion's motion import if used but missing."""
        if "motion." in content and "framer-motion" not in content:
            content = "import { motion } from 'framer-motion';\n" + content
            return content, True
        return content, False

    @staticmethod
    def _fix_lucide_icons_imports(content: str) -> tuple[str, bool]:
        """Auto-inject missing common Lucide-react icons."""
        common_icons = {
            "Github", "Linkedin", "Twitter", "Facebook", "Instagram", "Mail", "Phone", "MapPin", 
            "ExternalLink", "Download", "FileText", "Menu", "X", "ChevronDown", "ChevronUp", 
            "ChevronLeft", "ChevronRight", "Briefcase", "GraduationCap", "Award", "BookOpen", 
            "Code", "Server", "Database", "Cpu", "Globe", "Terminal", "User", "Settings", 
            "Sun", "Moon", "Calendar", "Heart", "Star", "Check", "AlertCircle", "Eye", "EyeOff", 
            "Sparkles", "ArrowRight", "ArrowLeft", "Send", "Clock", "Link"
        }
        tags = set(re.findall(r'<([A-Z][a-zA-Z0-9]*)\b', content))
        props = set(re.findall(r'\bicon\s*:\s*([A-Z][a-zA-Z0-9]*)\b', content))
        used_identifiers = tags.union(props)
        needed_icons = [icon for icon in common_icons if icon in used_identifiers]
        if not needed_icons:
            return content, False
            
        imported_icons = set()
        import_lines = []
        pattern = re.compile(r"import\s*\{([^}]+)\}\s*from\s*['\"]lucide-react['\"];?")
        for match in pattern.finditer(content):
            raw_names = [n.strip() for n in match.group(1).split(",") if n.strip()]
            imported_icons.update(raw_names)
            import_lines.append(match.group(0))
            
        missing_icons = [icon for icon in needed_icons if icon not in imported_icons]
        if not missing_icons:
            return content, False
            
        if import_lines:
            first_import = import_lines[0]
            m = pattern.search(first_import)
            if m:
                current_icons_str = m.group(1).strip()
                new_icons_str = current_icons_str
                if not new_icons_str.endswith(",") and new_icons_str:
                    new_icons_str += ", "
                new_icons_str += ", ".join(missing_icons)
                new_import_line = f"import {{ {new_icons_str} }} from 'lucide-react';"
                content = content.replace(first_import, new_import_line, 1)
        else:
            icons_str = ", ".join(missing_icons)
            content = f"import {{ {icons_str} }} from 'lucide-react';\n" + content
            
        return content, True

    @staticmethod
    def _sanitize_package_versions(files: dict[str, str]) -> tuple[dict[str, str], list[PreflightIssue]]:
        issues: list[PreflightIssue] = []
        out = dict(files)
        pkg_raw = out.get("package.json", "")
        if not pkg_raw:
            return out, issues
            
        try:
            pkg = json.loads(pkg_raw)
        except Exception:
            return out, issues
            
        changed = False
        safe_versions = {
            "autoprefixer": "^10.4.19",
            "tailwindcss": "^3.4.4",
            "postcss": "^8.4.38",
            "framer-motion": "^11.2.10",
            "lucide-react": "^0.395.0",
            "react-icons": "^5.2.1",
            "react-router-dom": "^6.24.0"
        }
        
        for dep_type in ["dependencies", "devDependencies"]:
            deps = pkg.get(dep_type, {})
            if isinstance(deps, dict):
                for pkg_name, safe_version in safe_versions.items():
                    if pkg_name in deps and deps[pkg_name] != safe_version:
                        deps[pkg_name] = safe_version
                        changed = True
                        
        if changed:
            out["package.json"] = json.dumps(pkg, indent=2) + "\n"
            issues.append(PreflightIssue("sanitized_package_versions", "Forced stable versions for core dependencies"))
            
        return out, issues

    @staticmethod
    def _apply_pre_build_fixups(files: dict[str, str]) -> tuple[dict[str, str], list[PreflightIssue]]:
        issues: list[PreflightIssue] = []
        out = dict(files)

        # 0) Sanitize package versions
        out, pkg_issues = PreflightRunner._sanitize_package_versions(out)
        issues.extend(pkg_issues)

        # 1) Fix obvious icon imports
        out, icon_issues = PreflightRunner._fix_common_icon_imports(out)
        issues.extend(icon_issues)

        # 2) Fix common JSX syntax and missing imports
        for path, content in list(out.items()):
            if not (path.endswith(".js") or path.endswith(".jsx") or path.endswith(".ts") or path.endswith(".tsx")):
                continue
            if not isinstance(content, str):
                continue
            
            changed = False
            
            content, self_closed = PreflightRunner._fix_jsx_void_tags(content)
            if self_closed:
                changed = True
                issues.append(PreflightIssue("self_closed_tags", f"Self-closed unclosed void tags in {path}"))
                
            content, hooks_imported = PreflightRunner._fix_react_hooks_imports(content)
            if hooks_imported:
                changed = True
                issues.append(PreflightIssue("added_hooks_imports", f"Added missing React hooks imports in {path}"))
                
            content, motion_imported = PreflightRunner._fix_framer_motion_imports(content)
            if motion_imported:
                changed = True
                issues.append(PreflightIssue("added_motion_imports", f"Added missing Framer Motion import in {path}"))
                
            content, lucide_imported = PreflightRunner._fix_lucide_icons_imports(content)
            if lucide_imported:
                changed = True
                issues.append(PreflightIssue("added_lucide_imports", f"Added/updated Lucide-react imports in {path}"))
                
            if changed:
                out[path] = content

        return out, issues

    @staticmethod
    async def run_preflight(
        *,
        files: dict[str, Any] | None,
        job_id: str,
    ) -> dict[str, str]:
        # Normalize first (also injects tailwind/index fixes)
        normalized = ReactProjectFormatter.normalize(files)

        # Apply deterministic fixups before static validation/build
        normalized, _fix_issues = PreflightRunner._apply_pre_build_fixups(normalized)

        static_issues = PreflightRunner._static_validate(normalized)
        if static_issues:
            raise PreflightError("Static validation failed", issues=static_issues)

        if not PreflightRunner._should_run_build():
            return normalized

        install_timeout_s, build_timeout_s = PreflightRunner._timeouts()

        staging_root = PreflightRunner._staging_root()
        staging_dir = Path(tempfile.mkdtemp(prefix=f"job-{job_id[:8]}-", dir=str(staging_root)))

        try:
            PreflightRunner._write_files(staging_dir, normalized)

            # Ensure npm is available
            npm = shutil.which("npm")
            if not npm:
                raise PreflightError("npm not found on PATH (required for preflight option 2)")

            # Install + build
            # Use npm ci if package-lock exists; otherwise npm install
            install_cmd = [npm, "install"]
            if (staging_dir / "package-lock.json").is_file():
                install_cmd = [npm, "ci"]

            rc, out = await PreflightRunner._run_cmd(install_cmd, cwd=staging_dir, timeout_s=install_timeout_s)
            if rc != 0:
                raise PreflightError(
                    "npm install failed",
                    issues=[PreflightIssue("npm_install_failed", out[-4000:])],
                )

            rc, out = await PreflightRunner._run_cmd([npm, "run", "build"], cwd=staging_dir, timeout_s=build_timeout_s)
            if rc != 0:
                # try to extract missing module lines to be helpful
                missing = []
                for line in out.splitlines():
                    if re.search(r"Cannot find module|Failed to resolve import|ERR_MODULE_NOT_FOUND", line):
                        missing.append(line.strip())
                msg = "\n".join(missing[:10]) if missing else out[-4000:]
                raise PreflightError(
                    "npm run build failed",
                    issues=[PreflightIssue("npm_build_failed", msg)],
                )

            return normalized

        except asyncio.TimeoutError as exc:
            raise PreflightError(
                "Preflight timed out",
                issues=[PreflightIssue("timeout", str(exc))],
            ) from exc
        finally:
            # Always cleanup staging dir unless explicitly kept
            keep = (os.getenv("PREFLIGHT_KEEP_STAGING", "0") or "").strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            if not keep:
                shutil.rmtree(staging_dir, ignore_errors=True)
