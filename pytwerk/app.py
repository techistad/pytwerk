from __future__ import annotations

from pathlib import Path

from flask import Flask

from pytwerk.compilers import CompilerBackend
from pytwerk.core import load_twerk_config
from pytwerk.frameworks.flask import create_flask_app, register_flask_route


def create_app(
    component_file: str | Path,
    *,
    component: str = "Home",
    title: str = "PyTwerk App",
    include_tailwind: bool = True,
    global_css: str = "",
    compiler_backend: CompilerBackend = "auto",
    rust_binary: str = "pytwerk-rs",
    allow_rust_fallback: bool = True,
) -> Flask:
    """
    Backward-compatible wrapper that creates a Flask app from one component file.
    """
    return create_flask_app(
        component_file,
        component=component,
        title=title,
        include_tailwind=include_tailwind,
        global_css=global_css,
        compiler_backend=compiler_backend,
        rust_binary=rust_binary,
        allow_rust_fallback=allow_rust_fallback,
    )


def create_project_app(
    project_root: str | Path,
    *,
    compiler_backend: CompilerBackend | None = None,
    rust_binary: str | None = None,
    allow_rust_fallback: bool | None = None,
) -> Flask:
    root = Path(project_root).resolve()
    config = load_twerk_config(root)

    app_cfg = config.get("app", {})
    compiler_cfg = config.get("compiler", {})
    pages_cfg = config.get("pages", {})
    styles_cfg = config.get("styles", {})
    static_cfg = config.get("static", {})
    external_links = config.get("external_links", [])

    backend = str(
        compiler_backend if compiler_backend is not None else compiler_cfg.get("backend", "auto")
    )
    rust_bin = str(
        rust_binary if rust_binary is not None else compiler_cfg.get("rust_binary", "pytwerk-rs")
    )
    rust_fallback = bool(
        allow_rust_fallback
        if allow_rust_fallback is not None
        else compiler_cfg.get("allow_rust_fallback", True)
    )

    static_dir = static_cfg.get("dir", "public")
    static_url_path = static_cfg.get("url_path", "/public")

    app = Flask(
        __name__,
        static_folder=str(root / str(static_dir)),
        static_url_path=str(static_url_path),
    )

    register_flask_route(
        app,
        str(pages_cfg.get("home_route", "/")),
        root / str(pages_cfg.get("home_component_file", "src/home.py")),
        component=str(pages_cfg.get("home_component", "Home")),
        title=str(app_cfg.get("title", "PyTwerk App")),
        include_tailwind=bool(styles_cfg.get("tailwind", True)),
        global_css=_read_global_css(root, str(styles_cfg.get("global_css_file", "src/styles/global.css"))),
        compiler_backend=backend,  # type: ignore[arg-type]
        rust_binary=rust_bin,
        allow_rust_fallback=rust_fallback,
    )

    _register_internal_api_routes(
        app,
        external_links=external_links if isinstance(external_links, list) else [],
    )
    return app


def get_project_run_options(project_root: str | Path) -> dict[str, object]:
    config = load_twerk_config(Path(project_root).resolve())
    server_cfg = config.get("server", {})
    return {
        "host": str(server_cfg.get("host", "127.0.0.1")),
        "port": int(server_cfg.get("port", 5000)),
        "debug": bool(server_cfg.get("debug", True)),
    }


def _read_global_css(project_root: Path, path_str: str) -> str:
    css_path = project_root / path_str
    if not css_path.exists():
        return ""
    return css_path.read_text(encoding="utf-8")


def _register_internal_api_routes(
    app: Flask,
    *,
    external_links: list[dict[str, str]],
) -> None:
    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "framework": "pytwerk"}

    @app.get("/api/meta")
    def meta() -> dict[str, object]:
        return {
            "project": "pytwerk-app",
            "external_links": external_links,
        }
