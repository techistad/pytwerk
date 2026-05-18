from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScaffoldResult:
    root: Path
    git_initialized: bool
    git_error: str | None = None


def scaffold_app(
    destination: str,
    *,
    init_git: bool = True,
) -> ScaffoldResult:
    root = Path(destination).resolve()
    app_name = root.name.replace("-", " ").replace("_", " ").title() or "PyTwerk App"

    _create_directories(
        root,
        [
            "public",
            "src",
            "src/components",
            "src/styles",
            "pages",
            "tests",
        ],
    )

    _write_if_missing(
        root / "src" / "home.py",
        """from src.app import App
from src.components import About, HeroSection


def Home():
    app_cfg = CONFIG.get("app", {})
    links = CONFIG.get("external_links", [])
    title = app_cfg.get("title", "PyTwerk App")
    content = f"{HeroSection(title=title)}{About(links=links)}"
    return App(raw_html(content))
""",
    )

    _write_if_missing(
        root / "src" / "app.py",
        """def App(content: object):
    app_cfg = CONFIG.get("app", {})
    title = app_cfg.get("title", "PyTwerk App")

    return (
        <main class="min-h-screen bg-slate-100">
            <section class="px-6 pt-10 pb-4">
                <div class="mx-auto w-[92%] max-w-5xl">
                    <p class="text-xs uppercase tracking-[0.16em] text-slate-500">PyTwerk Layout</p>
                    <p class="mt-2 text-slate-700">App shell for {title}</p>
                </div>
            </section>
            {raw_html(str(content))}
        </main>
    )
""",
    )

    _write_if_missing(
        root / "pages" / "about.py",
        """def AboutPage():
    app_cfg = CONFIG.get("app", {})
    title = app_cfg.get("title", "PyTwerk App")

    return (
        <main class="min-h-screen bg-white px-6 py-16">
            <div class="mx-auto w-[92%] max-w-5xl">
                <h1 class="text-4xl font-black text-slate-900">About {title}</h1>
                <p class="mt-4 text-slate-600">
                    This file lives in pages/ as an additional route-style page module.
                </p>
            </div>
        </main>
    )
""",
    )

    _write_if_missing(
        root / "pages" / "blog.py",
        """def BlogPage():
    return (
        <main class="min-h-screen bg-white px-6 py-16">
            <div class="mx-auto w-[92%] max-w-5xl">
                <h1 class="text-4xl font-black text-slate-900">Blog</h1>
                <p class="mt-4 text-slate-600">Add blog list rendering here.</p>
            </div>
        </main>
    )
""",
    )

    _write_if_missing(
        root / "src" / "styles" / "global.css",
        """* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
}

body {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
}
""",
    )

    _write_if_missing(
        root / "run.py",
        """import sys
from pathlib import Path

sys.dont_write_bytecode = True

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
if (REPO_ROOT / "pytwerk").is_dir():
    repo_root_str = str(REPO_ROOT)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

from pytwerk.app import create_project_app, get_project_run_options

app = create_project_app(BASE_DIR)


if __name__ == "__main__":
    app.run(**get_project_run_options(BASE_DIR))
""",
    )

    _write_if_missing(
        root / "twerk.config.py",
        f"""CONFIG = {{
    "app": {{
        "name": "{root.name}",
        "title": "{app_name}",
        "description": "{app_name} built with PyTwerk",
    }},
    "server": {{
        "host": "127.0.0.1",
        "port": 5000,
        "debug": True,
    }},
    "compiler": {{
        "backend": "auto",  # auto | python | rust
        "rust_binary": "pytwerk-rs",
        "allow_rust_fallback": True,
    }},
    "pages": {{
        "home_route": "/",
        "home_component_file": "src/home.py",
        "home_component": "Home",
    }},
    "styles": {{
        "tailwind": True,
        "global_css_file": "src/styles/global.css",
    }},
    "static": {{
        "dir": "public",
        "url_path": "/public",
    }},
    "external_links": [
        {{"label": "PyTwerk", "href": "https://github.com/search?q=pytwerk"}},
        {{"label": "Flask Docs", "href": "https://flask.palletsprojects.com/"}},
        {{"label": "Django Docs", "href": "https://docs.djangoproject.com/"}},
    ],
}}
""",
    )

    _write_if_missing(
        root / "public" / "robots.txt",
        "User-agent: *\nDisallow:\n",
    )

    _write_if_missing(
        root / "public" / "favicon.svg",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#0f172a"/>
  <path d="M16 48V16h19c8 0 13 4 13 11 0 6-3 9-9 10l10 11H41l-9-10h-8v10H16zm8-17h10c4 0 6-1 6-4 0-3-2-4-6-4H24v8z" fill="#f8fafc"/>
</svg>
""",
    )

    _write_if_missing(
        root / "src" / "components" / "hero.py",
        """@component
def HeroSection(title: str):
    safe_title = text(title)

    return (
        <section class="px-6 pt-20 pb-10">
            <div class="mx-auto w-[92%] max-w-5xl bg-white rounded-2xl p-10 border border-slate-200 shadow-lg">
                <p class="text-sm uppercase tracking-[0.18em] text-slate-500">PyTwerk</p>
                <h1 class="mt-3 text-5xl font-black leading-tight text-slate-900">{safe_title}</h1>
                <p class="mt-4 text-slate-600 max-w-2xl">
                    App-level component composition, React style, but with Python + HTML.
                </p>
            </div>
        </section>
    )
""",
    )

    _write_if_missing(
        root / "src" / "components" / "about.py",
        """@component
def About(links: list[dict[str, str]] | None = None):
    safe_links = links or []
    rendered_links = []
    for item in safe_links:
        label = text(item.get("label", "Link"))
        href = text(item.get("href", "#"))
        rendered_links.append(
            f'<a class="underline decoration-slate-400 hover:decoration-slate-900" href="{href}" target="_blank" rel="noreferrer">{label}</a>'
        )
    links_html = " | ".join(rendered_links) if rendered_links else ""

    return (
        <section class="px-6 pb-16">
            <div class="mx-auto w-[92%] max-w-5xl bg-white rounded-2xl p-8 border border-slate-200">
                <h2 class="text-2xl font-bold text-slate-900">About This Starter</h2>
                <p class="mt-3 text-slate-600">
                    Build components in src/components and compose root content in src/home.py.
                </p>
                <p class="mt-4 text-sm text-slate-600">{raw_html(links_html)}</p>
            </div>
        </section>
    )
""",
    )
    _write_if_missing(
        root / "src" / "components" / "__init__.py",
        """from .about import About
from .hero import HeroSection

__all__ = ["About", "HeroSection"]
""",
    )
    _write_if_missing(
        root / "tests" / "test_health.py",
        """from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
if (REPO_ROOT / "pytwerk").is_dir():
    repo_root_str = str(REPO_ROOT)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

from pytwerk.app import create_project_app


def test_health():
    root = ROOT
    app = create_project_app(root)
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "framework": "pytwerk"}
""",
    )

    _write_if_missing(
        root / "requirements.txt",
        """flask>=3.0.0,<4.0.0
pytest>=8.0.0
""",
    )

    _write_if_missing(
        root / "pyproject.toml",
        f"""[project]
name = "{root.name}"
version = "0.1.0"
description = "{app_name} built with PyTwerk"
requires-python = ">=3.11"
dependencies = [
  "flask>=3.0.0,<4.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
""",
    )

    _write_if_missing(
        root / "pyrightconfig.json",
        """{
  "typeCheckingMode": "basic",
  "exclude": [
    "pages/**/*.py",
    "src/components/**/*.py",
    "src/app.py",
    "src/home.py"
  ]
}
""",
    )

    _write_if_missing(
        root / "ruff.toml",
        """line-length = 100
target-version = "py311"
exclude = ["pages/*.py", "src/components/*.py", "src/app.py", "src/home.py"]
""",
    )

    _write_if_missing(
        root / ".env.example",
        """PYTWERK_ENV=development
PYTWERK_HOST=127.0.0.1
PYTWERK_PORT=5000
""",
    )

    _write_if_missing(
        root / ".gitignore",
        """__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.ruff_cache/
.venv/
dist/
build/
*.egg-info/
""",
    )

    _write_if_missing(
        root / "README.md",
        f"""# {app_name}

Scaffolded with PyTwerk CLI.

## Structure

- `src/` app composition (`app.py`, `home.py`) + components + styles
- `pages/` additional page modules (`about.py`, `blog.py`, etc.)
- `public/` static assets
- `twerk.config.py` project configuration (Next/Vite style)

Engine note: inside PyTwerk-loaded files, `component`, `text`, `raw_html`, and
`import_component`, `load_twerk_config` are available automatically.

## Run

```bash
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.

## API

- `GET /api/health`
- `GET /api/meta`
""",
    )

    git_initialized = False
    git_error: str | None = None
    if init_git:
        git_initialized, git_error = _init_git_repository(root)

    return ScaffoldResult(
        root=root,
        git_initialized=git_initialized,
        git_error=git_error,
    )


def _create_directories(root: Path, dirs: list[str]) -> None:
    for rel_dir in dirs:
        (root / rel_dir).mkdir(parents=True, exist_ok=True)


def _write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _init_git_repository(root: Path) -> tuple[bool, str | None]:
    if (root / ".git").exists():
        return True, None

    try:
        result = subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return False, str(exc)

    if result.returncode == 0:
        return True, None

    fallback = subprocess.run(
        ["git", "init"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if fallback.returncode != 0:
        stderr = fallback.stderr.strip() or fallback.stdout.strip() or "git init failed."
        return False, stderr

    rename = subprocess.run(
        ["git", "branch", "-M", "main"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if rename.returncode != 0:
        stderr = rename.stderr.strip() or rename.stdout.strip() or "failed to rename branch."
        return True, f"Repository initialized, but branch rename failed: {stderr}"

    return True, None


def print_django_template(
    *,
    component_file: str,
    component: str,
    title: str,
    include_tailwind: bool,
    css_file: str | None,
    compiler_backend: str,
    rust_binary: str,
    allow_rust_fallback: bool,
) -> None:
    css_block = ""
    if css_file:
        css_path = Path(css_file)
        css_block = (
            f"global_css = Path(r\"{css_path.as_posix()}\").read_text(encoding=\"utf-8\")\n"
        )
    else:
        css_block = "global_css = \"\"\n"

    text = f"""# urls.py template generated by PyTwerk
from pathlib import Path
from django.contrib import admin
from django.urls import path

from pytwerk.frameworks.django import create_django_view

{css_block}
urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        create_django_view(
            r"{component_file}",
            component="{component}",
            title="{title}",
            include_tailwind={include_tailwind},
            global_css=global_css,
            compiler_backend="{compiler_backend}",
            rust_binary=r"{rust_binary}",
            allow_rust_fallback={allow_rust_fallback},
        ),
        name="home",
    ),
]
"""
    print(text)
