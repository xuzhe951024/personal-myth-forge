from __future__ import annotations

import contextlib
import http.server
import shutil
import socketserver
import subprocess
import threading
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def script_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    ios_root = root / "apps/mobile/ios"
    source_root = Path(__file__).resolve().parents[3]
    shutil.copytree(
        source_root / "apps/mobile/ios/Config",
        ios_root / "Config",
        ignore=shutil.ignore_patterns("Deployment.local.xcconfig"),
    )
    shutil.copytree(source_root / "apps/mobile/ios/scripts", ios_root / "scripts")
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    return root


def test_deploy_preflight_blocks_missing_local_values(script_repo: Path) -> None:
    result = run_preflight(script_repo)

    assert result.returncode == 2
    assert "Missing DEVELOPMENT_TEAM" in result.stderr


def test_deploy_preflight_blocks_loopback_backend(script_repo: Path) -> None:
    write_local_config(script_repo, backend_url="http://127.0.0.1:8080")

    result = run_preflight(script_repo)

    assert result.returncode == 2
    assert "not loopback" in result.stderr


def test_deploy_preflight_blocks_invalid_final_launch_mode(script_repo: Path) -> None:
    write_local_config(
        script_repo,
        backend_url="http://192.168.1.10:8080",
        final_launch_mode="live",
    )

    result = run_preflight(script_repo)

    assert result.returncode == 2
    assert "PMF_FINAL_LAUNCH_MODE must be local or configured." in result.stderr


def test_deploy_preflight_fails_tracked_local_config(script_repo: Path) -> None:
    write_local_config(script_repo, backend_url="http://192.168.1.10:8080")
    subprocess.run(
        ["git", "add", "apps/mobile/ios/Config/Deployment.local.xcconfig"],
        cwd=script_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_preflight(script_repo)

    assert result.returncode == 1
    assert "must stay untracked" in result.stderr


def test_deploy_preflight_passes_when_backend_health_is_ok(script_repo: Path) -> None:
    with health_server('{"status":"ok"}') as backend_url:
        write_local_config(script_repo, backend_url=backend_url)
        result = run_preflight(script_repo)

    assert result.returncode == 0
    assert "iOS deploy preflight passed." in result.stdout
    assert "Backend health: ok" in result.stdout


def test_deploy_preflight_passes_with_configured_final_launch_mode(
    script_repo: Path,
) -> None:
    with health_server('{"status":"ok"}') as backend_url:
        write_local_config(
            script_repo,
            backend_url=backend_url,
            final_launch_mode="configured",
        )
        result = run_preflight(script_repo)

    assert result.returncode == 0
    assert "Final launch mode: configured" in result.stdout


def test_deploy_preflight_blocks_non_ok_backend_without_leaking_body(script_repo: Path) -> None:
    body = '{"status":"down","secret":"sk-test","path":"/Users/zhexu/private"}'
    with health_server(body) as backend_url:
        write_local_config(script_repo, backend_url=backend_url)
        result = run_preflight(script_repo)

    assert result.returncode == 2
    assert "Backend health check failed." in result.stderr
    assert "sk-test" not in result.stderr
    assert "/Users/" not in result.stderr


def run_preflight(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["apps/mobile/ios/scripts/deploy_preflight.sh"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def write_local_config(
    root: Path,
    *,
    backend_url: str,
    team: str = "ABCDE12345",
    bundle_id: str = "com.example.personalmythforge",
    final_launch_mode: str | None = None,
) -> None:
    local_config = root / "apps/mobile/ios/Config/Deployment.local.xcconfig"
    lines = [
        f"DEVELOPMENT_TEAM = {team}",
        f"PRODUCT_BUNDLE_IDENTIFIER = {bundle_id}",
        f"PMF_BACKEND_BASE_URL = {backend_url}",
    ]
    if final_launch_mode is not None:
        lines.append(f"PMF_FINAL_LAUNCH_MODE = {final_launch_mode}")
    lines.append("")
    local_config.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


@contextlib.contextmanager
def health_server(body: str) -> Iterator[str]:
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path != "/health":
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def log_message(self, format: str, *args: object) -> None:
            return

    with socketserver.TCPServer(("127.0.0.1", 0), Handler) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://0.0.0.0:{port}"
        finally:
            server.shutdown()
            thread.join(timeout=5)
