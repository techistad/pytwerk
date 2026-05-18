from __future__ import annotations

from pathlib import Path
from typing import Any


def inject_engine_symbols(
    namespace: dict[str, object],
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> None:
    from pytwerk.core.component_loader import import_component
    from pytwerk.core.config import load_twerk_config
    from pytwerk.core.html import HtmlFragment, component, raw_html, text

    namespace.setdefault("component", component)
    namespace.setdefault("raw_html", raw_html)
    namespace.setdefault("text", text)
    namespace.setdefault("HtmlFragment", HtmlFragment)
    namespace.setdefault("import_component", import_component)
    namespace.setdefault("load_twerk_config", load_twerk_config)

    if project_root is not None:
        namespace.setdefault("PROJECT_ROOT", project_root)
        namespace.setdefault("BASE_DIR", project_root)
    if config is not None:
        namespace.setdefault("CONFIG", config)
