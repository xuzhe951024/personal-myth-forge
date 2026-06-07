from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def test_init_creates_missing_final_resources_from_template(tmp_path: Path) -> None:
    repo = _script_repo(tmp_path)

    result = _run_init(repo)

    destination = repo / "services/backend/.local/final-resources.env"
    template = repo / "services/backend/final-resources.env.example"
    assert result.returncode == 0
    assert destination.read_text(encoding="utf-8") == template.read_text(encoding="utf-8")
    assert "services/backend/.local/final-resources.env initialized" in result.stdout
    assert "make final-resources-preflight" in result.stdout
    assert "MESHY_API_KEY=" not in result.stdout + result.stderr


def test_init_refuses_to_overwrite_existing_final_resources(tmp_path: Path) -> None:
    repo = _script_repo(tmp_path)
    destination = repo / "services/backend/.local/final-resources.env"
    destination.parent.mkdir(parents=True)
    destination.write_text("MESHY_API_KEY=already-filled\n", encoding="utf-8")

    result = _run_init(repo)

    assert result.returncode == 2
    assert "already exists" in result.stderr
    assert destination.read_text(encoding="utf-8") == "MESHY_API_KEY=already-filled\n"
    assert "already-filled" not in result.stdout + result.stderr


def test_init_refuses_tracked_final_resources_destination(tmp_path: Path) -> None:
    repo = _script_repo(tmp_path)
    destination = repo / "services/backend/.local/final-resources.env"
    destination.parent.mkdir(parents=True)
    destination.write_text("MESHY_API_KEY=tracked-secret\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "services/backend/.local/final-resources.env"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    result = _run_init(repo)

    assert result.returncode == 1
    assert "must stay untracked" in result.stderr
    assert "tracked-secret" not in result.stdout + result.stderr


def test_makefile_exposes_final_resource_init_target() -> None:
    makefile = Path(__file__).resolve().parents[3] / "Makefile"
    text = makefile.read_text(encoding="utf-8")

    assert "final-resource-init:" in text
    assert "scripts/init_final_resources.sh" in text


def test_final_resource_template_keeps_user_specific_ios_values_empty() -> None:
    template = (
        Path(__file__).resolve().parents[3]
        / "services/backend/final-resources.env.example"
    )
    text = template.read_text(encoding="utf-8")

    assert "PRODUCT_BUNDLE_IDENTIFIER=\n" in text
    assert "PMF_BACKEND_BASE_URL=\n" in text
    assert "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge" not in text
    assert "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080" not in text


def _script_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    source_root = Path(__file__).resolve().parents[3]
    shutil.copytree(source_root / "services/backend/scripts", repo / "services/backend/scripts")
    (repo / "services/backend").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        source_root / "services/backend/final-resources.env.example",
        repo / "services/backend/final-resources.env.example",
    )
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _run_init(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", "services/backend/scripts/init_final_resources.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
