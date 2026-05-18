from __future__ import annotations

import argparse
from pathlib import Path

from pytwerk.frameworks.flask import create_flask_app
from pytwerk.templates import print_django_template, scaffold_app


def _read_css(css_file: str | None) -> str:
    if not css_file:
        return ""
    return Path(css_file).read_text(encoding="utf-8")


def _build_common_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--component", default="Home", help="Component function name.")
    parser.add_argument("--title", default="PyTwerk App", help="Document title.")
    parser.add_argument(
        "--compiler-backend",
        choices=["auto", "python", "rust"],
        default="auto",
        help="Compiler backend selection.",
    )
    parser.add_argument(
        "--rust-binary",
        default="pytwerk-rs",
        help="Rust compiler executable name or path.",
    )
    parser.add_argument(
        "--no-rust-fallback",
        action="store_true",
        help="When backend=auto, fail instead of falling back to Python compiler.",
    )
    parser.add_argument(
        "--no-tailwind",
        action="store_true",
        help="Disable Tailwind CDN injection.",
    )
    parser.add_argument(
        "--css-file",
        default=None,
        help="Path to global CSS file injected inside <style>.",
    )


def _run_flask(args: argparse.Namespace) -> None:
    app = create_flask_app(
        args.component_file,
        component=args.component,
        title=args.title,
        include_tailwind=not args.no_tailwind,
        global_css=_read_css(args.css_file),
        compiler_backend=args.compiler_backend,
        rust_binary=args.rust_binary,
        allow_rust_fallback=not args.no_rust_fallback,
    )
    app.run(host=args.host, port=args.port, debug=True)


def _run_django_template(args: argparse.Namespace) -> None:
    print_django_template(
        component_file=args.component_file,
        component=args.component,
        title=args.title,
        include_tailwind=not args.no_tailwind,
        css_file=args.css_file,
        compiler_backend=args.compiler_backend,
        rust_binary=args.rust_binary,
        allow_rust_fallback=not args.no_rust_fallback,
    )


def _run_new_app(args: argparse.Namespace) -> None:
    result = scaffold_app(args.destination, init_git=not args.no_git)
    print(f"Created PyTwerk starter app at: {result.root}")
    if args.no_git:
        print("Skipped git initialization (--no-git).")
    elif result.git_initialized:
        if result.git_error:
            print(f"Git initialized with warning: {result.git_error}")
        else:
            print("Git repository initialized on branch 'main'.")
    else:
        print(f"Git initialization failed: {result.git_error or 'unknown error'}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PyTwerk CLI: Flask runtime + Django integration templates."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve = subparsers.add_parser("serve", help="Run Flask server for a PyTwerk component.")
    serve.add_argument("component_file", help="Path to .py file with PyTwerk syntax.")
    serve.add_argument("--host", default="127.0.0.1", help="Flask host.")
    serve.add_argument("--port", default=5000, type=int, help="Flask port.")
    _build_common_parser(serve)
    serve.set_defaults(_handler=_run_flask)

    django_tpl = subparsers.add_parser(
        "django-template",
        help="Print a Django urls.py template for the selected component.",
    )
    django_tpl.add_argument("component_file", help="Path to .py file with PyTwerk syntax.")
    _build_common_parser(django_tpl)
    django_tpl.set_defaults(_handler=_run_django_template)

    new_app = subparsers.add_parser(
        "new-app",
        help="Scaffold a starter PyTwerk app folder.",
    )
    new_app.add_argument("destination", help="Folder to create starter app in.")
    new_app.add_argument(
        "--no-git",
        action="store_true",
        help="Skip automatic git initialization.",
    )
    new_app.set_defaults(_handler=_run_new_app)

    args = parser.parse_args()
    args._handler(args)


if __name__ == "__main__":
    main()
