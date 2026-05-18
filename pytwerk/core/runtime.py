from __future__ import annotations

import re
from html import escape
from typing import Any, Dict, Mapping

from .html import HtmlFragment

_EXPR_PATTERN = re.compile(r"\{([^{}]+)\}")
_COMPONENT_SELF_CLOSING_PATTERN = re.compile(r"<([A-Z][A-Za-z0-9_]*)\s*/>")
_COMPONENT_EMPTY_TAG_PATTERN = re.compile(r"<([A-Z][A-Za-z0-9_]*)\s*>\s*</\1>")


def __pytwerk_render__(
    template: str,
    local_context: Dict[str, Any],
    global_context: Mapping[str, Any] | None = None,
) -> str:
    globals_map = dict(global_context or {})
    rendered_template = _expand_component_tags(template, local_context, globals_map)

    def replacer(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        value = eval(expr, globals_map, local_context)
        if isinstance(value, HtmlFragment):
            return str(value)
        return escape(str(value))

    return _EXPR_PATTERN.sub(replacer, rendered_template)


def build_document(
    body_html: str,
    *,
    title: str = "PyTwerk App",
    include_tailwind: bool = True,
    global_css: str = "",
) -> str:
    tailwind = (
        '<script src="https://cdn.tailwindcss.com"></script>' if include_tailwind else ""
    )
    style_block = f"<style>{global_css}</style>" if global_css.strip() else ""

    return (
        "<!doctype html>"
        "<html lang='en'>"
        "<head>"
        "<meta charset='utf-8' />"
        "<meta name='viewport' content='width=device-width, initial-scale=1' />"
        f"<title>{escape(title)}</title>"
        f"{tailwind}"
        f"{style_block}"
        "</head>"
        "<body>"
        f"{body_html}"
        "</body>"
        "</html>"
    )


def _expand_component_tags(
    template: str,
    local_context: Mapping[str, Any],
    global_context: Mapping[str, Any],
) -> str:
    def render_component(name: str) -> str | None:
        candidate = local_context.get(name, global_context.get(name))
        if candidate is None or not callable(candidate):
            return None
        value = candidate()
        if isinstance(value, HtmlFragment):
            return str(value)
        return escape(str(value))

    def replace_empty_tag(match: re.Match[str]) -> str:
        rendered = render_component(match.group(1))
        return rendered if rendered is not None else match.group(0)

    def replace_self_closing_tag(match: re.Match[str]) -> str:
        rendered = render_component(match.group(1))
        return rendered if rendered is not None else match.group(0)

    current = template
    while True:
        expanded = _COMPONENT_EMPTY_TAG_PATTERN.sub(replace_empty_tag, current)
        expanded = _COMPONENT_SELF_CLOSING_PATTERN.sub(replace_self_closing_tag, expanded)
        if expanded == current:
            break
        current = expanded
    return current
