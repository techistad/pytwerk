from __future__ import annotations

from functools import wraps
from html import escape
from typing import Any, Callable, TypeVar


class HtmlFragment(str):
    """
    Trusted HTML fragment.

    Values of this type are rendered without escaping.
    """


F = TypeVar("F", bound=Callable[..., Any])


def raw_html(value: str) -> HtmlFragment:
    return HtmlFragment(value)


def text(value: Any) -> str:
    """
    Escape plain text for safe HTML insertion.
    """
    return escape(str(value))


def component(func: F) -> F:
    """
    Mark a function as a component that returns trusted HTML fragments.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> HtmlFragment:
        value = func(*args, **kwargs)
        if isinstance(value, HtmlFragment):
            return value
        return HtmlFragment(str(value))

    return wrapper  # type: ignore[return-value]
