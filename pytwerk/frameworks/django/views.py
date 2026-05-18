from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pytwerk.compilers import CompilerBackend
from pytwerk.core.loader import load_module_from_file
from pytwerk.core.runtime import build_document


def create_django_view(
    component_file: str | Path,
    *,
    component: str = "Home",
    title: str = "PyTwerk App",
    include_tailwind: bool = True,
    global_css: str = "",
    compiler_backend: CompilerBackend = "auto",
    rust_binary: str = "pytwerk-rs",
    allow_rust_fallback: bool = True,
) -> Callable[[Any], Any]:
    try:
        from django.http import HttpResponse
    except ImportError as exc:
        raise RuntimeError(
            "Django is not installed. Install it with `pip install django`."
        ) from exc

    def view(_request: Any) -> Any:
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
            return HttpResponse(
                (
                    f"Component '{component}' not found in {component_file}. "
                    f"Available callables: {available}"
                ),
                status=500,
                content_type="text/plain",
            )

        body = component_fn()
        html = build_document(
            body,
            title=title,
            include_tailwind=include_tailwind,
            global_css=global_css,
        )
        return HttpResponse(html, content_type="text/html")

    return view
