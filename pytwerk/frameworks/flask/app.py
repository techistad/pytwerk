from __future__ import annotations

from pathlib import Path

from flask import Flask

from pytwerk.compilers import CompilerBackend
from .routing import register_flask_route


def create_flask_app(
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
    app = Flask(__name__)
    register_flask_route(
        app,
        "/",
        component_file,
        component=component,
        title=title,
        include_tailwind=include_tailwind,
        global_css=global_css,
        compiler_backend=compiler_backend,
        rust_binary=rust_binary,
        allow_rust_fallback=allow_rust_fallback,
    )
    return app
