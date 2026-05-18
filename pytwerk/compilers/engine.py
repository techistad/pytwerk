from __future__ import annotations

from . import python_backend, rust_backend
from .types import CompilationResult, CompilerBackend


def compile_component_source(
    source: str,
    *,
    backend: CompilerBackend = "auto",
    rust_binary: str = "pytwerk-rs",
    allow_rust_fallback: bool = True,
) -> CompilationResult:
    if backend == "python":
        return CompilationResult(
            compiled_source=python_backend.compile_source(source),
            backend="python",
        )

    if backend == "rust":
        return CompilationResult(
            compiled_source=rust_backend.compile_source(source, rust_binary=rust_binary),
            backend="rust",
        )

    if backend == "auto":
        try:
            compiled = rust_backend.compile_source(source, rust_binary=rust_binary)
            return CompilationResult(compiled_source=compiled, backend="rust")
        except rust_backend.RustCompilerUnavailableError:
            if not allow_rust_fallback:
                raise
            return CompilationResult(
                compiled_source=python_backend.compile_source(source),
                backend="python",
            )

    raise ValueError(
        f"Unsupported compiler backend '{backend}'. Use one of: auto, python, rust."
    )
