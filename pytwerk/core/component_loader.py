from __future__ import annotations

from pathlib import Path
from typing import Callable

from pytwerk.compilers import CompilerBackend
from .loader import load_module_from_file


def import_component(
    component_file: str | Path,
    component: str,
    *,
    compiler_backend: CompilerBackend = "auto",
    rust_binary: str = "pytwerk-rs",
    allow_rust_fallback: bool = True,
) -> Callable[..., object]:
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
        raise ValueError(
            f"Component '{component}' not found in {component_file}. "
            f"Available callables: {available}"
        )
    return component_fn
