"""PyTwerk: Python-first HTML component framework."""

from .app import create_app, create_project_app, get_project_run_options
from .compilers import CompilationResult, compile_component_source
from .compilers.python_backend import compile_source
from .core import (
    HtmlFragment,
    component,
    discover_project_root,
    import_component,
    load_twerk_config,
    raw_html,
    text,
)
from .frameworks.django import DjangoRoute, create_django_urlpatterns, create_django_view
from .frameworks.flask import create_flask_app, register_flask_route

__all__ = [
    "CompilationResult",
    "DjangoRoute",
    "HtmlFragment",
    "compile_component_source",
    "compile_source",
    "component",
    "create_app",
    "create_project_app",
    "create_django_urlpatterns",
    "create_django_view",
    "create_flask_app",
    "get_project_run_options",
    "discover_project_root",
    "import_component",
    "load_twerk_config",
    "raw_html",
    "register_flask_route",
    "text",
]
