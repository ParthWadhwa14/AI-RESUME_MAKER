from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReactProjectFormatter:
    """Normalizes a generated file-map into the expected Vite+React scaffold.

    The LLM sometimes returns paths like `/App.js` for Sandpack (CRA-style) or
    omits the full Vite scaffold. This helper merges the generated output into
    the provided `react_template.json` scaffold used by the crew.

    It also ensures that any downloaded assets written to `/public/...` end up
    in the right place.
    """

    @staticmethod
    def _load_scaffold() -> dict[str, str]:
        # backend/app/services/react_project_formatter.py -> backend
        backend_dir = Path(__file__).resolve().parents[2]
        template_path = (
            backend_dir
            / "website_maker"
            / "src"
            / "website_maker"
            / "config"
            / "react_template.json"
        )
        if not template_path.is_file():
            return {}
        return json.loads(template_path.read_text(encoding="utf-8"))

    @staticmethod
    def _is_esm_project(out: dict[str, str]) -> bool:
        pkg_raw = out.get("package.json", "")
        try:
            pkg = json.loads(pkg_raw) if pkg_raw else {}
        except Exception:
            return False
        return pkg.get("type") == "module"

    @staticmethod
    def _ensure_postcss_and_tailwind_configs(out: dict[str, str]) -> None:
        """Ensure Tailwind + PostCSS configs exist and match the project's module type.

        Vite (Node) loads PostCSS config according to package.json "type".
        If "type":"module", a `postcss.config.js` with `module.exports` will crash.
        """
        uses_tailwind = any(
            token in "\n".join(out.get(p, "") for p in ("src/App.jsx", "src/App.tsx", "src/main.jsx", "src/main.tsx"))
            for token in ("bg-", "text-", "flex", "grid", "px-", "py-", "mt-", "mb-", "rounded", "shadow")
        )
        
        # We must process the renaming logic if the files exist in `out`, 
        # even if we didn't detect tailwind usage in the root components.
        has_config = "postcss.config.js" in out or "tailwind.config.js" in out or "postcss.config.cjs" in out or "tailwind.config.cjs" in out
        
        if not uses_tailwind and not has_config:
            return

        is_esm = ReactProjectFormatter._is_esm_project(out)

        # PostCSS config
        if is_esm:
            if "postcss.config.js" in out:
                out["postcss.config.cjs"] = out.pop("postcss.config.js")
            else:
                out.setdefault(
                    "postcss.config.cjs",
                    "module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n};\n",
                )
            out.pop("postcss.config.js", None)
        else:
            if "postcss.config.cjs" in out:
                out["postcss.config.js"] = out.pop("postcss.config.cjs")
            else:
                out.setdefault(
                    "postcss.config.js",
                    "module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n};\n",
                )
            out.pop("postcss.config.cjs", None)

        # Tailwind config
        if is_esm:
            if "tailwind.config.js" in out:
                out["tailwind.config.cjs"] = out.pop("tailwind.config.js")
            else:
                out.setdefault(
                    "tailwind.config.cjs",
                    "module.exports = {\n  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],\n  theme: { extend: {} },\n  plugins: [],\n};\n",
                )
            out.pop("tailwind.config.js", None)
        else:
            if "tailwind.config.cjs" in out:
                out["tailwind.config.js"] = out.pop("tailwind.config.cjs")
            else:
                out.setdefault(
                    "tailwind.config.js",
                    "module.exports = {\n  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],\n  theme: { extend: {} },\n  plugins: [],\n};\n",
                )
            out.pop("tailwind.config.cjs", None)

        # Normalize config file references inside all configuration/code files (e.g. vite.config.js)
        for filename in list(out.keys()):
            if filename.endswith(".js") or filename.endswith(".jsx") or filename.endswith(".ts") or filename.endswith(".tsx") or filename == "package.json":
                content = out[filename]
                if is_esm:
                    content = content.replace("postcss.config.js", "postcss.config.cjs")
                    content = content.replace("tailwind.config.js", "tailwind.config.cjs")
                else:
                    content = content.replace("postcss.config.cjs", "postcss.config.js")
                    content = content.replace("tailwind.config.cjs", "tailwind.config.js")
                out[filename] = content

    @staticmethod
    def _ensure_tailwind_enabled(out: dict[str, str]) -> None:
        """If Tailwind classes are present, ensure Tailwind directives exist."""
        combined = "\n".join(
            out.get(p, "")
            for p in (
                "src/App.jsx",
                "src/App.tsx",
                "src/main.jsx",
                "src/main.tsx",
            )
        )
        uses_tailwind = any(
            token in combined
            for token in (
                "bg-",
                "text-",
                "flex",
                "grid",
                "px-",
                "py-",
                "mt-",
                "mb-",
                "rounded",
                "shadow",
            )
        )
        if not uses_tailwind:
            return

        styles_path = "src/styles.css"
        styles = out.get(styles_path, "")
        if "@tailwind base" not in styles:
            out[styles_path] = (
                "@tailwind base;\n"
                "@tailwind components;\n"
                "@tailwind utilities;\n\n"
                + styles.strip()
                + "\n"
            )

        # Ensure PostCSS/Tailwind config exists and matches ESM/CJS expectations
        ReactProjectFormatter._ensure_postcss_and_tailwind_configs(out)

    @staticmethod
    def _ensure_index_html_valid(out: dict[str, str]) -> None:
        """Repair common parse5-breaking meta tag mistakes and missing module types in index.html."""
        # This is a safe fallback to keep projects runnable.
        html = out.get("index.html")
        if not html or "<html" not in html:
            return
            
        # Ensure script tag has type="module" which Vite requires
        import re
        html = re.sub(r'<script\s+src="([^"]+)"', r'<script type="module" src="\1"', html)
        html = re.sub(r"<script\s+src='([^']+)'", r"<script type='module' src='\1'", html)
        out["index.html"] = html
        
        # If a meta tag line is missing a closing ">" it often contains '<meta ' without a closing '/>' or '>'
        # Rather than fragile parsing, reset to known-good scaffold while preserving the title if present.
        if "<meta" in html and "/>" not in html and "</meta>" not in html:
            # Leave as-is; it might still be valid. Only reset on obvious broken cases.
            pass
        broken_signals = [
            "<meta name=\"description\"",
            "<meta property=\"og:",
        ]
        if any(sig in html and ">" not in line and "/>" not in line for sig in broken_signals for line in html.splitlines()):
            out["index.html"] = (
                "<!doctype html>\n"
                "<html lang=\"en\">\n"
                "  <head>\n"
                "    <meta charset=\"UTF-8\" />\n"
                "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
                "    <title>Portfolio</title>\n"
                "  </head>\n"
                "  <body>\n"
                "    <div id=\"root\"></div>\n"
                "    <script type=\"module\" src=\"/src/main.jsx\"></script>\n"
                "  </body>\n"
                "</html>\n"
            )

    @staticmethod
    def _strip_common_llm_wrappers(text: str) -> str:
        """Best-effort cleanup for common model wrappers around JSON."""
        if not isinstance(text, str):
            return str(text)
        s = text.strip()
        # Remove markdown fences
        if s.startswith("```"):
            lines = s.splitlines()
            # drop first fence line
            if lines:
                lines = lines[1:]
            # drop last fence line if present
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            s = "\n".join(lines).strip()
        # Extract first JSON object if extra text exists
        if "{" in s and "}" in s:
            start = s.find("{")
            end = s.rfind("}")
            if start >= 0 and end > start:
                s = s[start : end + 1]
        return s.strip()

    @staticmethod
    def _default_package_json(*, include_tailwind: bool) -> dict[str, Any]:
        deps = {
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "framer-motion": "^12.23.12",
            "lucide-react": "^0.525.0",
        }
        dev_deps = {
            "vite": "^5.4.19",
            "@vitejs/plugin-react": "^4.3.4",
        }
        if include_tailwind:
            dev_deps.update(
                {
                    "tailwindcss": "^3.4.17",
                    "postcss": "^8.4.49",
                    "autoprefixer": "^10.4.20",
                }
            )
        return {
            "name": "resume-gala-portfolio",
            "private": True,
            "version": "0.0.1",
            "type": "module",
            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
            "dependencies": deps,
            "devDependencies": dev_deps,
        }

    @staticmethod
    def _ensure_package_json_valid(out: dict[str, str]) -> None:
        """Guarantee package.json exists and is valid JSON.

        Preflight fails hard if package.json is invalid; the model sometimes outputs
        markdown fences or extra commentary. Here we sanitize and fall back to a
        known-good scaffold.
        """
        # Detect Tailwind usage from code (same heuristic as Tailwind enabling)
        combined = "\n".join(
            out.get(p, "") for p in ("src/App.jsx", "src/App.tsx", "src/main.jsx", "src/main.tsx")
        )
        uses_tailwind = any(
            token in combined
            for token in ("bg-", "text-", "flex", "grid", "px-", "py-", "mt-", "mb-", "rounded", "shadow")
        )

        raw = out.get("package.json")
        raw = ReactProjectFormatter._strip_common_llm_wrappers(raw) if raw else ""

        pkg: dict[str, Any] | None = None
        if raw:
            try:
                pkg = json.loads(raw)
            except Exception:
                pkg = None

        if not isinstance(pkg, dict):
            # Fall back to default known-good
            pkg = ReactProjectFormatter._default_package_json(include_tailwind=uses_tailwind)

        # Ensure required scripts
        scripts = pkg.get("scripts") if isinstance(pkg.get("scripts"), dict) else {}
        scripts.setdefault("dev", "vite")
        scripts.setdefault("build", "vite build")
        scripts.setdefault("preview", "vite preview")
        pkg["scripts"] = scripts

        # Ensure required deps used by scaffold quality bar
        deps = pkg.get("dependencies") if isinstance(pkg.get("dependencies"), dict) else {}
        deps.setdefault("react", "^18.3.1")
        deps.setdefault("react-dom", "^18.3.1")
        deps.setdefault("framer-motion", "^12.23.12")
        deps.setdefault("lucide-react", "^0.525.0")
        pkg["dependencies"] = deps

        dev_deps = pkg.get("devDependencies") if isinstance(pkg.get("devDependencies"), dict) else {}
        dev_deps.setdefault("vite", "^5.4.19")
        dev_deps.setdefault("@vitejs/plugin-react", "^4.3.4")
        if uses_tailwind:
            dev_deps.setdefault("tailwindcss", "^3.4.17")
            dev_deps.setdefault("postcss", "^8.4.49")
            dev_deps.setdefault("autoprefixer", "^10.4.20")
        pkg["devDependencies"] = dev_deps

        pkg.setdefault("private", True)
        pkg.setdefault("name", "resume-gala-portfolio")
        pkg.setdefault("version", "0.0.1")
        pkg.setdefault("type", "module")

        out["package.json"] = json.dumps(pkg, ensure_ascii=False, indent=2) + "\n"

    @staticmethod
    def normalize(files: dict[str, Any] | None) -> dict[str, str]:
        files = files or {}

        # Coerce everything to string content
        str_files: dict[str, str] = {
            (k if str(k).startswith("/") else f"/{k}"): (v if isinstance(v, str) else str(v))
            for k, v in files.items()
        }

        scaffold = ReactProjectFormatter._load_scaffold()
        out: dict[str, str] = {}

        # Start with scaffold (already uses paths like "src/App.jsx" etc)
        for path, content in (scaffold or {}).items():
            out[path.lstrip("/")] = content

        # Overlay generated output
        for path, content in str_files.items():
            clean = path.lstrip("/")

            # Common Sandpack/CRA style root App -> Vite src/App.jsx
            if clean in {"App.js", "App.jsx"}:
                out["src/App.jsx"] = content
                continue

            # Common root index -> Vite src/main.jsx
            if clean in {"index.js", "index.jsx", "main.js", "main.jsx"}:
                out["src/main.jsx"] = content
                continue

            out[clean] = content

        # Ensure required entrypoints exist
        out.setdefault(
            "src/main.jsx",
            "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\nimport './styles.css';\n\nReactDOM.createRoot(document.getElementById('root')).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);\n",
        )
        out.setdefault(
            "src/App.jsx",
            "export default function App() {\n  return <h1>Generated portfolio</h1>;\n}\n",
        )

        # Make package.json robust before dependent checks
        ReactProjectFormatter._ensure_package_json_valid(out)

        # Hardening steps to reduce runtime failures
        ReactProjectFormatter._ensure_tailwind_enabled(out)
        ReactProjectFormatter._ensure_index_html_valid(out)

        return out
