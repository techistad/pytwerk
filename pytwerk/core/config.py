from __future__ import annotations

from pathlib import Path
import runpy
from typing import Any


def discover_project_root(
    start: str | Path,
    *,
    filename: str = "twerk.config.py",
) -> Path:
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / filename).exists():
            return candidate
    return current


def load_twerk_config(
    base_dir: str | Path,
    *,
    filename: str = "twerk.config.py",
) -> dict[str, Any]:
    root = Path(base_dir).resolve()
    config_file = root / filename
    if not config_file.exists():
        return {}
    loaded = runpy.run_path(str(config_file))
    config = loaded.get("CONFIG", {})
    if not isinstance(config, dict):
        raise TypeError(f"CONFIG in {filename} must be a dictionary.")
    return config
