from __future__ import annotations

import ast
import subprocess
from pathlib import Path
import sys


class RustCompilerError(RuntimeError):
    """Raised when the Rust compiler bridge fails."""


class RustCompilerUnavailableError(RustCompilerError):
    """Raised when the Rust compiler executable is unavailable."""


def compile_source(source: str, *, rust_binary: str = "pytwerk-rs") -> str:
    """
    Compile source through Rust compiler bridge.

    Contract for the Rust binary:
    - command: `<binary> compile --stdin`
    - stdin: raw PyTwerk source
    - stdout: compiled valid Python source
    """
    commands = _resolve_commands(rust_binary)
    result = None
    launch_errors: list[str] = []

    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                input=source,
                text=True,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            continue
        except OSError as exc:
            launch_errors.append(f"{cmd[0]}: {exc}")
            continue
        else:
            break

    if result is None:
        error_suffix = ""
        if launch_errors:
            error_suffix = " Launch errors: " + "; ".join(launch_errors)
        raise RustCompilerUnavailableError(
            f"Rust compiler command is unavailable for '{rust_binary}'.{error_suffix}"
        )

    if result.returncode != 0:
        stderr = result.stderr.strip() or "no stderr output"
        raise RustCompilerError(
            f"Rust compiler returned exit code {result.returncode}: {stderr}"
        )

    compiled = result.stdout
    if not compiled.strip():
        raise RustCompilerError("Rust compiler returned empty output.")

    ast.parse(compiled)
    return compiled if compiled.endswith("\n") else f"{compiled}\n"


def _resolve_commands(rust_binary: str) -> list[list[str]]:
    if rust_binary != "pytwerk-rs":
        return [[rust_binary, "compile", "--stdin"]]

    root = Path(__file__).resolve().parents[2]
    manifest_path = root / "rust" / "pytwerk-rs" / "Cargo.toml"
    local_debug_binary = root / "rust" / "pytwerk-rs" / "target" / "debug" / (
        "pytwerk-rs.exe" if _is_windows() else "pytwerk-rs"
    )

    commands: list[list[str]] = [[rust_binary, "compile", "--stdin"]]

    if manifest_path.exists():
        commands.append(
            [
                "cargo",
                "run",
                "--quiet",
                "--manifest-path",
                str(manifest_path),
                "--",
                "compile",
                "--stdin",
            ]
        )

    if local_debug_binary.exists():
        commands.append([str(local_debug_binary), "compile", "--stdin"])

    return commands


def _is_windows() -> bool:
    return sys.platform.startswith("win")
