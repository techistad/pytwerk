from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pytwerk.compilers import CompilerBackend
from .views import create_django_view


@dataclass(frozen=True)
class DjangoRoute:
    route: str
    component_file: str | Path
    component: str = "Home"
    name: str | None = None
    title: str = "PyTwerk App"


def create_django_urlpatterns(
    routes: list[DjangoRoute],
    *,
    include_tailwind: bool = True,
    global_css: str = "",
    compiler_backend: CompilerBackend = "auto",
    rust_binary: str = "pytwerk-rs",
    allow_rust_fallback: bool = True,
) -> list[Any]:
    try:
        from django.urls import path
    except ImportError as exc:
        raise RuntimeError(
            "Django is not installed. Install it with `pip install django`."
        ) from exc

    patterns: list[Any] = []
    for route in routes:
        view = create_django_view(
            route.component_file,
            component=route.component,
            title=route.title,
            include_tailwind=include_tailwind,
            global_css=global_css,
            compiler_backend=compiler_backend,
            rust_binary=rust_binary,
            allow_rust_fallback=allow_rust_fallback,
        )
        patterns.append(path(route.route, view, name=route.name))
    return patterns
