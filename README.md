# PyTwerk

PyTwerk is a Python-first component framework where HTML and Python logic live in the same component file.

Phase 1 now includes:
- Flask runtime adapter.
- Django adapter helpers.
- Dual compiler backend architecture:
  - Python compiler backend.
  - Rust compiler backend (`pytwerk-rs`) with auto fallback.

## Component syntax

```python
def Home():
    name = "Ankan"
    return (
        <h1>Hello {name}</h1>
    )
```

## Component composition

You can compose components across files:

```python
@component
def Card(title: str):
    heading = text(title)
    return (
        <section><h2>{heading}</h2></section>
    )
```

```python
from src.components import Card

def Home():
    return (
        <main>{Card("Welcome")}</main>
    )
```

`component`, `text`, `raw_html`, `import_component`, and `load_twerk_config` are injected by the engine in PyTwerk-loaded files.
For zero-argument components, you can also render with self-closing tags like `<Card />`.

## Professional package layout

```text
pytwerk/
  apis/
  cli/
  compilers/
  core/
  frameworks/
    django/
    flask/
  templates/
  app.py              # top-level Flask app convenience entrypoint
rust/
  pytwerk-rs/         # Rust compiler binary crate
examples/
```

## Install

```bash
pip install -r requirements.txt
```

## Flask run (primary runtime)

```bash
python -m pytwerk serve examples/hello.py --component Home --css-file examples/global.css
```

Open `http://127.0.0.1:5000`.

### Compiler backend selection

- Auto (default): tries Rust first, then Python fallback.
- Force Python:

```bash
python -m pytwerk serve examples/hello.py --compiler-backend python
```

- Force Rust:

```bash
python -m pytwerk serve examples/hello.py --compiler-backend rust
```

## Django integration template

Generate a ready `urls.py` template:

```bash
python -m pytwerk django-template examples/hello.py --component Home
```

## Scaffold a starter app

```bash
python -m pytwerk new-app ./my-pytwerk-app
```

Generated app structure:

```text
my-pytwerk-app/
  app/
  public/
  src/
  pages/
  twerk.config.py
  .gitignore
  README.md
  requirements.txt
  pyproject.toml
```

By default this command also runs `git init` and sets the initial branch to `main`.
Use `--no-git` to skip repository initialization.

## Rust compiler crate

Rust compiler source lives in `rust/pytwerk-rs`.

Build it:

```bash
cargo build --manifest-path rust/pytwerk-rs/Cargo.toml
```

By default, PyTwerk can also run Rust backend via `cargo run` if binary is not prebuilt.

## Run smoke tests

```bash
python -m unittest -v tests/test_smoke.py
```

## Editor warning suppression for syntax demo files

- `pyrightconfig.json` ignores `examples/**/*.py`.
- `ruff.toml` excludes `examples/*.py`.

This keeps IDE diagnostics clean for raw PyTwerk syntax files.
