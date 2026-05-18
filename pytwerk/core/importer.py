from __future__ import annotations

import importlib.abc
import importlib.machinery
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from pytwerk.compilers import CompilerBackend, compile_component_source
from pytwerk.compilers.python_backend import is_pytwerk_source
from pytwerk.core.config import load_twerk_config
from pytwerk.core.symbols import inject_engine_symbols


@dataclass(frozen=True)
class _ImportSettings:
    project_root: Path
    compiler_backend: CompilerBackend
    rust_binary: str
    allow_rust_fallback: bool


class _PyTwerkSourceLoader(importlib.machinery.SourceFileLoader):
    def __init__(
        self,
        fullname: str,
        path: str,
        settings: _ImportSettings,
    ) -> None:
        super().__init__(fullname, path)
        self._settings = settings

    def exec_module(self, module: ModuleType) -> None:
        config = load_twerk_config(self._settings.project_root)
        inject_engine_symbols(
            module.__dict__,
            config=config,
            project_root=self._settings.project_root,
        )
        super().exec_module(module)

    def source_to_code(self, data: bytes, path: str, *, _optimize: int = -1):  # type: ignore[override]
        try:
            source = data.decode("utf-8")
        except UnicodeDecodeError:
            return super().source_to_code(data, path, _optimize=_optimize)

        if not is_pytwerk_source(source):
            return super().source_to_code(data, path, _optimize=_optimize)

        compilation = compile_component_source(
            source,
            backend=self._settings.compiler_backend,
            rust_binary=self._settings.rust_binary,
            allow_rust_fallback=self._settings.allow_rust_fallback,
        )
        return compile(
            compilation.compiled_source,
            path,
            "exec",
            dont_inherit=True,
            optimize=_optimize,
        )


class _PyTwerkMetaPathFinder(importlib.abc.MetaPathFinder):
    def __init__(self) -> None:
        self._registrations: dict[str, _ImportSettings] = {}

    def register(self, settings: _ImportSettings) -> None:
        key = str(settings.project_root)
        self._registrations[key] = settings

    def find_spec(self, fullname: str, path=None, target=None):  # type: ignore[override]
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec is None or spec.origin is None:
            return spec

        origin = Path(spec.origin)
        if origin.suffix != ".py":
            return spec

        if not isinstance(spec.loader, importlib.machinery.SourceFileLoader):
            return spec

        settings = self._resolve_settings(origin)
        if settings is None:
            return spec

        spec.loader = _PyTwerkSourceLoader(fullname, spec.origin, settings)
        return spec

    def _resolve_settings(self, origin: Path) -> _ImportSettings | None:
        for settings in self._registrations.values():
            if _is_within(origin, settings.project_root):
                return settings
        return None


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


_FINDER: _PyTwerkMetaPathFinder | None = None


def install_pytwerk_importer(
    *,
    project_root: Path,
    compiler_backend: CompilerBackend,
    rust_binary: str,
    allow_rust_fallback: bool,
) -> None:
    global _FINDER

    settings = _ImportSettings(
        project_root=project_root.resolve(),
        compiler_backend=compiler_backend,
        rust_binary=rust_binary,
        allow_rust_fallback=allow_rust_fallback,
    )

    if _FINDER is None:
        _FINDER = _PyTwerkMetaPathFinder()
        sys.meta_path.insert(0, _FINDER)

    _FINDER.register(settings)
