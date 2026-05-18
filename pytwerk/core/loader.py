from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

from pytwerk.compilers import CompilerBackend, compile_component_source
from pytwerk.compilers.python_backend import is_pytwerk_source
from pytwerk.core.config import discover_project_root, load_twerk_config
from pytwerk.core.importer import install_pytwerk_importer
from pytwerk.core.symbols import inject_engine_symbols


def load_module_from_file(
    filepath: str | Path,
    *,
    compiler_backend: CompilerBackend = "auto",
    rust_binary: str = "pytwerk-rs",
    allow_rust_fallback: bool = True,
) -> ModuleType:
    path = Path(filepath).resolve()
    source = path.read_text(encoding="utf-8")
    project_root = discover_project_root(path.parent)
    config = load_twerk_config(project_root)

    install_pytwerk_importer(
        project_root=project_root,
        compiler_backend=compiler_backend,
        rust_binary=rust_binary,
        allow_rust_fallback=allow_rust_fallback,
    )

    compiled_source = source
    active_backend = "python"
    if is_pytwerk_source(source):
        compilation = compile_component_source(
            source,
            backend=compiler_backend,
            rust_binary=rust_binary,
            allow_rust_fallback=allow_rust_fallback,
        )
        compiled_source = compilation.compiled_source
        active_backend = compilation.backend

    if not compiled_source.endswith("\n"):
        compiled_source += "\n"

    module = ModuleType(path.stem)
    module.__file__ = str(path.resolve())
    module.__pytwerk_compiler__ = active_backend
    inject_engine_symbols(
        module.__dict__,
        config=config,
        project_root=project_root,
    )
    _ensure_module_import_scope(path.parent, project_root)
    exec(compiled_source, module.__dict__)
    return module


def _ensure_module_import_scope(directory: Path, project_root: Path) -> None:
    """
    Ensure local imports for the component file remain available at render time.
    """
    candidates = [
        directory.resolve(),
        (project_root / "src").resolve(),
        (project_root / "pages").resolve(),
        project_root.resolve(),
    ]
    for candidate in reversed(candidates):
        candidate_str = str(candidate)
        if candidate_str in sys.path:
            continue
        sys.path.insert(0, candidate_str)
