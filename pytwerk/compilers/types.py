from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CompilerBackend = Literal["auto", "python", "rust"]


@dataclass(frozen=True)
class CompilationResult:
    compiled_source: str
    backend: str
