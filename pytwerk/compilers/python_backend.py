from __future__ import annotations

import ast
from typing import List


def is_pytwerk_source(source: str) -> bool:
    lines = source.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() != "return (":
            i += 1
            continue

        j = i + 1
        markup_lines: List[str] = []
        while j < len(lines):
            candidate = lines[j]
            if candidate.strip() == ")":
                break
            markup_lines.append(candidate)
            j += 1

        first_non_empty = ""
        for raw in markup_lines:
            if raw.strip():
                first_non_empty = raw.strip()
                break

        if j < len(lines) and markup_lines and first_non_empty.startswith("<"):
            return True

        i += 1

    return False


def compile_source(source: str) -> str:
    """
    Compile PyTwerk syntax into valid Python.

    Supported syntax (phase 1):

    return (
        <h1>Hello {name}</h1>
    )
    """
    lines = source.splitlines()
    out: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "return (":
            indent = line[: len(line) - len(line.lstrip())]
            j = i + 1
            markup_lines: List[str] = []

            while j < len(lines):
                candidate = lines[j]
                if candidate.strip() == ")":
                    break
                markup_lines.append(candidate)
                j += 1

            first_non_empty = ""
            for raw in markup_lines:
                if raw.strip():
                    first_non_empty = raw.strip()
                    break

            if j < len(lines) and markup_lines and first_non_empty.startswith("<"):
                markup = "\n".join(markup_lines).strip("\n")
                out.append(f"{indent}return __pytwerk_render__(")
                out.append(f"{indent}    {markup!r},")
                out.append(f"{indent}    locals(),")
                out.append(f"{indent}    globals(),")
                out.append(f"{indent})")
                i = j + 1
                continue

        out.append(line)
        i += 1

    compiled = "\n".join(out)
    prelude = "from pytwerk.core.runtime import __pytwerk_render__\n\n"
    final = prelude + compiled + ("\n" if not compiled.endswith("\n") else "")
    ast.parse(final)
    return final
