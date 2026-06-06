import json

from myth_forge_api.capture_acceptance import run_capture_3d_acceptance
from myth_forge_api.providers.three_d import LocalThreeDProvider, ThreeDGenerationRequest


class RecordingThreeDProvider:
    provider_name = "recording"

    def __init__(self) -> None:
        self.requests: list[ThreeDGenerationRequest] = []
        self.local_provider = LocalThreeDProvider()

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        self.requests.append(request)
        return self.local_provider.generate_game_asset(request)


def test_capture_3d_acceptance_runs_guided_scan_source_images(tmp_path) -> None:
    result = run_capture_3d_acceptance(capture_storage_dir=tmp_path / "captures")

    report_text = json.dumps(result.report)
    assert result.exit_code == 0
    assert result.report["kind"] == "capture_3d_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["capture_mode"] == "guided_scan"
    assert result.report["capture_media_count"] == 3
    assert result.report["source_image_count"] == 3
    assert result.report["source_asset_count"] == 0
    assert result.report["provider_request_source_image_count"] == 3
    assert result.report["provider_request_source_asset_count"] == 0
    assert result.report["generation_provenance"]["input_mode"] == "multi_image"
    assert result.report["generation_provenance"]["source_image_count"] == 3
    assert result.report["generation_provenance"]["selected_source_image_count"] == 3
    assert result.report["scene_loadable_variant"] is True
    assert result.report["safety"]["raw_media_in_report"] is False
    assert result.report["safety"]["local_paths_in_report"] is False
    assert result.report["safety"]["provider_secrets_in_report"] is False
    assert "data:image" not in report_text
    assert "local-capture://" not in report_text
    assert str(tmp_path) not in report_text


def test_capture_3d_acceptance_passes_source_images_to_provider(tmp_path) -> None:
    provider = RecordingThreeDProvider()

    result = run_capture_3d_acceptance(
        capture_storage_dir=tmp_path / "captures",
        three_d_provider=provider,
    )

    assert result.exit_code == 0
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert len(request.source_images) == 3
    assert len(request.source_assets) == 0
    assert [image.content_type for image in request.source_images] == [
        "image/jpeg",
        "image/png",
        "image/png",
    ]
    assert all(
        image.data_uri.startswith(f"data:{image.content_type};base64,")
        for image in request.source_images
    )


class FailingThreeDProvider:
    provider_name = "failing"

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        raise RuntimeError(
            "failed data:image/png;base64,AAAA "
            "local-capture://cap_0123456789abcdef/media_0.png "
            "/tmp/personal-myth-forge/private.png "
            "Authorization=Bearer provider-secret raw=private"
        )


def test_capture_3d_acceptance_sanitizes_failure_report(tmp_path) -> None:
    result = run_capture_3d_acceptance(
        capture_storage_dir=tmp_path / "captures",
        three_d_provider=FailingThreeDProvider(),
    )

    report_text = json.dumps(result.report)
    assert result.exit_code == 1
    assert result.report["status"] == "failed"
    assert "data:image" not in report_text
    assert "local-capture://" not in report_text
    assert "provider-secret" not in report_text
    assert "Authorization" not in report_text
    assert str(tmp_path) not in report_text
