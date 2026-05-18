from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
if (REPO_ROOT / "pytwerk").is_dir():
    repo_root_str = str(REPO_ROOT)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

from pytwerk.app import create_project_app


def test_health():
    root = ROOT
    app = create_project_app(root)
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "framework": "pytwerk"}
