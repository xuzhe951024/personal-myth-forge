from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from dotenv import dotenv_values

from myth_forge_api.config import load_settings


FULL_RESOURCES = """# Final demo resources. Do not commit the filled copy.
MESHY_API_KEY=meshy-secret-test
OPENAI_API_KEY=sk-openai-test
OPENAI_API_BASE_URL=https://api.openai.test/v1
PRINT_PROVIDER=treatstock
TREATSTOCK_API_KEY=treatstock-secret-test
TREATSTOCK_API_BASE_URL=https://treatstock.test
SCULPTEO_API_KEY=
DEVELOPMENT_TEAM=ABCDE12345
PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge
PMF_BACKEND_BASE_URL=http://192.168.1.10:8080
CAPTURE_STORAGE_DIR=
MYTH_SESSION_STORAGE_DIR=
"""


@pytest.fixture
def script_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    source_root = Path(__file__).resolve().parents[3]
    shutil.copytree(source_root / "services/backend/scripts", root / "services/backend/scripts")
    shutil.copytree(source_root / "apps/mobile/ios/scripts", root / "apps/mobile/ios/scripts")
    shutil.copytree(source_root / "apps/mobile/ios/Config", root / "apps/mobile/ios/Config")
    (root / "services/backend").mkdir(parents=True, exist_ok=True)
    template = source_root / "services/backend/final-resources.env.example"
    if template.exists():
        shutil.copy2(template, root / "services/backend/final-resources.env.example")
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    return root


def test_apply_blocks_missing_default_resources_file(script_repo: Path) -> None:
    result = run_apply(script_repo)

    assert result.returncode == 2
    assert "Missing final resources file" in result.stderr
    assert not backend_env_path(script_repo).exists()
    assert not ios_local_config_path(script_repo).exists()


def test_apply_blocks_unknown_key_without_writing_outputs(script_repo: Path) -> None:
    resources = write_resources(script_repo, FULL_RESOURCES + "UNKNOWN_PROVIDER_KEY=value\n")

    result = run_apply(script_repo, "--resources-file", str(resources))

    assert result.returncode == 2
    assert "Unknown final resource key: UNKNOWN_PROVIDER_KEY" in result.stderr
    assert not backend_env_path(script_repo).exists()
    assert not ios_local_config_path(script_repo).exists()
    assert "meshy-secret-test" not in result.stdout + result.stderr


def test_apply_blocks_loopback_backend_without_writing_outputs(script_repo: Path) -> None:
    resources = write_resources(
        script_repo,
        FULL_RESOURCES.replace(
            "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
            "PMF_BACKEND_BASE_URL=http://127.0.0.1:8080",
        ),
    )

    result = run_apply(script_repo, "--resources-file", str(resources))

    assert result.returncode == 2
    assert "PMF_BACKEND_BASE_URL must be reachable from iPhone" in result.stderr
    assert not backend_env_path(script_repo).exists()
    assert not ios_local_config_path(script_repo).exists()


def test_apply_requires_treatstock_key_when_treatstock_is_selected(
    script_repo: Path,
) -> None:
    resources = write_resources(
        script_repo,
        FULL_RESOURCES.replace("TREATSTOCK_API_KEY=treatstock-secret-test\n", ""),
    )

    result = run_apply(script_repo, "--resources-file", str(resources))

    assert result.returncode == 2
    assert "TREATSTOCK_API_KEY is required when PRINT_PROVIDER=treatstock" in result.stderr
    assert not backend_env_path(script_repo).exists()
    assert not ios_local_config_path(script_repo).exists()


def test_apply_blocks_unsupported_final_launch_mode_without_writing_outputs(
    script_repo: Path,
) -> None:
    resources = write_resources(script_repo, FULL_RESOURCES + "PMF_FINAL_LAUNCH_MODE=live\n")

    result = run_apply(script_repo, "--resources-file", str(resources))

    assert result.returncode == 2
    assert "Unsupported PMF_FINAL_LAUNCH_MODE in final resources: live" in result.stderr
    assert not backend_env_path(script_repo).exists()
    assert not ios_local_config_path(script_repo).exists()


def test_apply_writes_final_launch_mode_to_ios_config(script_repo: Path) -> None:
    resources = write_resources(
        script_repo,
        FULL_RESOURCES + "PMF_FINAL_LAUNCH_MODE=configured\n",
    )

    result = run_apply(script_repo, "--resources-file", str(resources))

    assert result.returncode == 0
    ios_text = ios_local_config_path(script_repo).read_text(encoding="utf-8")
    assert "PMF_FINAL_LAUNCH_MODE = configured" in ios_text


def test_apply_writes_backend_and_ios_configs_with_redacted_output(
    script_repo: Path,
) -> None:
    resources = write_resources(script_repo, FULL_RESOURCES)

    result = run_apply(script_repo, "--resources-file", str(resources))

    combined_output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Final resources applied." in result.stdout
    assert "services/backend/.env written." in result.stdout
    assert "Deployment.local.xcconfig written." in result.stdout
    assert "MESHY_API_KEY: configured (redacted)" in result.stdout
    assert "OPENAI_API_KEY: configured (redacted)" in result.stdout
    assert "TREATSTOCK_API_KEY: configured (redacted)" in result.stdout
    assert "meshy-secret-test" not in combined_output
    assert "sk-openai-test" not in combined_output
    assert "treatstock-secret-test" not in combined_output

    backend_text = backend_env_path(script_repo).read_text(encoding="utf-8")
    ios_text = ios_local_config_path(script_repo).read_text(encoding="utf-8")
    assert "THREE_D_PROVIDER=meshy" in backend_text
    assert "MESHY_API_KEY=meshy-secret-test" in backend_text
    assert "NPC_PROVIDER=openai" in backend_text
    assert "OPENAI_API_KEY=sk-openai-test" in backend_text
    assert "PRINT_PROVIDER=treatstock" in backend_text
    assert "TREATSTOCK_API_KEY=treatstock-secret-test" in backend_text
    assert "TREATSTOCK_API_BASE_URL=https://treatstock.test" in backend_text
    assert "DEVELOPMENT_TEAM = ABCDE12345" in ios_text
    assert "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge" in ios_text
    assert "PMF_BACKEND_BASE_URL = http://192.168.1.10:8080" in ios_text


def test_apply_output_can_be_loaded_as_final_settings(
    script_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resources = write_resources(script_repo, FULL_RESOURCES)

    result = run_apply(script_repo, "--resources-file", str(resources))

    assert result.returncode == 0
    raw_values = dotenv_values(backend_env_path(script_repo))
    settings = load_settings(env={key: value or "" for key, value in raw_values.items()})
    assert settings.three_d_provider == "meshy"
    assert settings.meshy_api_key == "meshy-secret-test"
    assert settings.npc_provider == "openai"
    assert settings.openai_api_key == "sk-openai-test"
    assert settings.print_provider == "treatstock"
    assert settings.treatstock_api_key == "treatstock-secret-test"
    assert settings.treatstock_api_base_url == "https://treatstock.test"


def run_apply(
    root: Path,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", "services/backend/scripts/apply_final_resources.sh", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
    )


def write_resources(root: Path, text: str) -> Path:
    path = root / "services/backend/.local/final-resources.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def backend_env_path(root: Path) -> Path:
    return root / "services/backend/.env"


def ios_local_config_path(root: Path) -> Path:
    return root / "apps/mobile/ios/Config/Deployment.local.xcconfig"
