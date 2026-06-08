from __future__ import annotations

import json

from myth_forge_api.local_showcase_smoke import build_local_showcase_smoke_report


def test_local_showcase_smoke_runs_full_http_loop() -> None:
    result = build_local_showcase_smoke_report()

    assert result.exit_code == 0
    assert result.report["kind"] == "local_showcase_smoke_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {
        "passed": 10,
        "failed": 0,
        "http_steps": 6,
        "npc_ticks": 2,
        "downloads": 3,
    }
    steps = {step["id"]: step for step in result.report["steps"]}
    assert list(steps) == [
        "upload_guided_scan_capture",
        "create_session_from_capture",
        "download_game_asset",
        "download_scene_asset",
        "run_npc_autonomy",
        "create_print_quote",
        "download_print_asset",
        "history_contains_ticks",
        "generation_provenance",
        "report_safety",
    ]
    assert all(step["status"] == "passed" for step in steps.values())
    assert result.report["session"]["generated_asset_provider"] == "local_stub"
    assert result.report["session"]["generation_input_mode"] == "multi_image"
    assert result.report["session"]["scene_variant_format"] == "dae"
    assert result.report["session"]["npc_agent_runtime"] == "local_agent_runtime"
    assert result.report["npc"]["completed_steps"] == 2
    assert result.report["print"]["quote_status"] == "draft_quote"
    assert result.report["downloads"]["game_glb"]["content_proof"] == "glTF"
    assert result.report["downloads"]["scene_dae"]["content_proof"] == "COLLADA"
    assert result.report["downloads"]["print_3mf"]["content_proof"] == "PK"
    assert result.report["safety"] == {
        "provider_calls": False,
        "live_provider_calls": False,
        "global_mutation": False,
        "starts_server": False,
        "writes_repo_local_media": False,
        "uses_temporary_storage": True,
        "provider_secrets_in_report": False,
        "raw_media_in_report": False,
        "local_paths_in_report": False,
        "payment_links_in_report": False,
    }
    report_text = json.dumps(result.report)
    assert "data:image" not in report_text
    assert "local-capture://" not in report_text
    assert "/tmp" not in report_text
    assert "/Users/" not in report_text


def test_local_showcase_smoke_fails_when_first_http_step_fails() -> None:
    result = build_local_showcase_smoke_report(client_factory=lambda: FailingClient())

    report_text = json.dumps(result.report)
    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert result.report["summary"]["failed"] == 1
    assert result.report["steps"][0]["id"] == "upload_guided_scan_capture"
    assert result.report["steps"][0]["status"] == "failed"
    assert "raw=private" not in report_text
    assert "Internal Server Error" not in report_text


def test_local_showcase_smoke_sanitizes_unsafe_failure_text() -> None:
    unsafe = (
        "Authorization=Bearer sk-local data:image/png;base64,AAAA "
        "/tmp/private checkout_url https://pay.example/abc"
    )
    result = build_local_showcase_smoke_report(
        client_factory=lambda: FailingClient(text=unsafe),
    )

    report_text = json.dumps(result.report)
    assert result.exit_code == 1
    assert "[withheld]" in report_text
    assert "sk-local" not in report_text
    assert "Authorization" not in report_text
    assert "data:image" not in report_text
    assert "/tmp" not in report_text
    assert "checkout_url" not in report_text
    assert "pay.example" not in report_text


class FailingClient:
    def __init__(self, text: str = "Internal Server Error raw=private") -> None:
        self.text = text

    def post(self, *_args, **_kwargs) -> "FakeResponse":
        return FakeResponse(status_code=500, text=self.text)

    def get(self, *_args, **_kwargs) -> "FakeResponse":
        return FakeResponse(status_code=500, text=self.text)


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int,
        text: str = "",
        payload: dict[str, object] | None = None,
        content: bytes = b"",
    ) -> None:
        self.status_code = status_code
        self.text = text
        self._payload = payload or {}
        self.content = content

    def json(self) -> dict[str, object]:
        return self._payload
