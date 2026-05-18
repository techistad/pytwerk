import sys
from pathlib import Path

sys.dont_write_bytecode = True

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
if (REPO_ROOT / "pytwerk").is_dir():
    repo_root_str = str(REPO_ROOT)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

from pytwerk.app import create_project_app, get_project_run_options

app = create_project_app(BASE_DIR)


if __name__ == "__main__":
    app.run(**get_project_run_options(BASE_DIR))
