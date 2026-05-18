from __future__ import annotations

from pathlib import Path

from flask import Flask

from pytwerk.compilers import CompilerBackend
from pytwerk.core.loader import load_module_from_file
from pytwerk.core.runtime import build_document


def register_flask_route(
    app: Flask,
    route: str,
    component_file: str | Path,
    *,
    component: str = "Home",
    title: str = "PyTwerk App",
    include_tailwind: bool = True,
    global_css: str = "",
    compiler_backend: CompilerBackend = "auto",
    rust_binary: str = "pytwerk-rs",
    allow_rust_fallback: bool = True,
) -> None:
    endpoint_name = f"pytwerk_{component}_{route.strip('/').replace('/', '_') or 'root'}"

    @app.get(route, endpoint=endpoint_name)
    def _route() -> str:
        module = load_module_from_file(
            component_file,
            compiler_backend=compiler_backend,
            rust_binary=rust_binary,
            allow_rust_fallback=allow_rust_fallback,
        )
        component_fn = getattr(module, component, None)
        if component_fn is None or not callable(component_fn):
            available = ", ".join(
                name for name, value in module.__dict__.items() if callable(value)
            )
            return (
                f"Component '{component}' not found in {component_file}. "
                f"Available callables: {available}",
                500,
            )

        body = component_fn()
        return build_document(
            body,
            title=title,
            include_tailwind=include_tailwind,
            global_css=global_css,
        )
