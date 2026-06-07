import os
import subprocess
from pathlib import Path

from myth_forge_api.source_freshness import git_product_source_metadata


def test_git_product_source_metadata_handles_relative_repo_root_from_nested_cwd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace = tmp_path / "workspace"
    repo_root = _init_git_repo(workspace)
    backend_cwd = repo_root / "services/backend"
    backend_cwd.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(backend_cwd)

    metadata = git_product_source_metadata(Path("../.."))

    assert metadata is not None
    assert metadata.revision
    assert metadata.source_scope["kind"] == "git_product_sources"
    assert "services/backend/src" in metadata.source_scope["paths"]


def test_git_product_source_metadata_returns_none_for_relative_non_repo(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace = tmp_path / "workspace"
    non_repo = workspace / "not-a-repo"
    nested_cwd = workspace / "nested"
    non_repo.mkdir(parents=True)
    nested_cwd.mkdir()
    monkeypatch.chdir(nested_cwd)

    assert git_product_source_metadata(Path("../not-a-repo")) is None


def _init_git_repo(workspace: Path) -> Path:
    repo_root = workspace / "repo"
    repo_root.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_root,
        check=True,
    )
    (repo_root / "Makefile").write_text("backend-test:\n\tpytest\n", encoding="utf-8")
    src_dir = repo_root / "services/backend/src"
    src_dir.mkdir(parents=True)
    (src_dir / "app.py").write_text("print('ok')\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "Makefile", "services/backend/src/app.py"],
        cwd=repo_root,
        check=True,
    )
    env = os.environ | {
        "GIT_AUTHOR_DATE": "2026-06-07T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-06-07T12:00:00+00:00",
    }
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_root,
        check=True,
        env=env,
        capture_output=True,
    )
    return repo_root
