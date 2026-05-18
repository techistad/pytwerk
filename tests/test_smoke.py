from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pytwerk.app import create_app
from pytwerk.compilers import compile_component_source
from pytwerk.compilers.rust_backend import RustCompilerError, RustCompilerUnavailableError
from pytwerk.templates import scaffold_app


ROOT = Path(__file__).resolve().parents[1]
HELLO_COMPONENT = ROOT / "examples" / "hello.py"


class PyTwerkSmokeTests(unittest.TestCase):
    def test_python_compiler_backend(self) -> None:
        source = HELLO_COMPONENT.read_text(encoding="utf-8")
        result = compile_component_source(source, backend="python")
        self.assertEqual(result.backend, "python")
        self.assertIn("return __pytwerk_render__(", result.compiled_source)

    def test_flask_render_with_python_backend(self) -> None:
        app = create_app(str(HELLO_COMPONENT), component="Home", compiler_backend="python")
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello Ankan", response.get_data(as_text=True))

    def test_rust_backend_when_available(self) -> None:
        source = HELLO_COMPONENT.read_text(encoding="utf-8")
        try:
            result = compile_component_source(source, backend="rust")
        except (RustCompilerUnavailableError, RustCompilerError):
            self.skipTest("Rust backend unavailable in this environment.")
            return
        self.assertEqual(result.backend, "rust")
        self.assertIn("return __pytwerk_render__(", result.compiled_source)

    def test_new_app_scaffold_layout(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "demo_app"
            result = scaffold_app(str(project_root), init_git=False)

            self.assertEqual(result.root, project_root.resolve())
            self.assertFalse(result.git_initialized)
            self.assertFalse((project_root / ".git").exists())

            expected_dirs = [
                "public",
                "src",
                "pages",
                "tests",
            ]
            for rel_dir in expected_dirs:
                self.assertTrue((project_root / rel_dir).is_dir(), rel_dir)

            expected_files = [
                ".gitignore",
                "README.md",
                "pyproject.toml",
                "requirements.txt",
                "run.py",
                "pages/about.py",
                "pages/blog.py",
                "src/app.py",
                "src/home.py",
                "src/components/hero.py",
                "src/components/about.py",
                "tests/test_health.py",
                "twerk.config.py",
            ]
            for rel_file in expected_files:
                self.assertTrue((project_root / rel_file).is_file(), rel_file)

            app_page_source = (project_root / "src" / "app.py").read_text(encoding="utf-8")
            home_source = (project_root / "src" / "home.py").read_text(encoding="utf-8")
            about_page_source = (project_root / "pages" / "about.py").read_text(encoding="utf-8")
            blog_page_source = (project_root / "pages" / "blog.py").read_text(encoding="utf-8")
            config_source = (project_root / "twerk.config.py").read_text(encoding="utf-8")
            run_source = (project_root / "run.py").read_text(encoding="utf-8")

            self.assertIn("def App(content: object):", app_page_source)
            self.assertIn("from src.app import App", home_source)
            self.assertIn("from src.components import About, HeroSection", home_source)
            self.assertNotIn("Path(__file__)", app_page_source)
            self.assertNotIn("import_component(", app_page_source)
            self.assertFalse((project_root / "src" / "__init__.py").exists())
            self.assertFalse((project_root / "tests" / "__init__.py").exists())
            self.assertIn('def AboutPage():', about_page_source)
            self.assertIn('def BlogPage():', blog_page_source)
            self.assertIn('"home_component_file": "src/home.py"', config_source)
            self.assertIn('"home_component": "Home"', config_source)
            self.assertIn("create_project_app(BASE_DIR)", run_source)
            self.assertIn("get_project_run_options(BASE_DIR)", run_source)

    def test_component_import_and_composition(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "parts").mkdir(parents=True, exist_ok=True)
            (root / "twerk.config.py").write_text("CONFIG = {}\n", encoding="utf-8")
            (root / "parts" / "badge.py").write_text(
                """@component
def Badge():
    label = "Ankan"
    safe = text(label)
    return (
        <strong class="badge">{safe}</strong>
    )
""",
                encoding="utf-8",
            )
            page_file = root / "page.py"
            page_file.write_text(
                """from parts.badge import Badge


def Home():
    return (
        <div>Hello <Badge /></div>
    )
""",
                encoding="utf-8",
            )

            app = create_app(page_file, component="Home", compiler_backend="python")
            client = app.test_client()
            response = client.get("/")
            body = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<strong class="badge">Ankan</strong>', body)
            self.assertNotIn("&lt;strong class=", body)


if __name__ == "__main__":
    unittest.main()
