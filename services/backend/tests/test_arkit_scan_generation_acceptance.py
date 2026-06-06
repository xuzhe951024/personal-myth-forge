import json

from myth_forge_api.arkit_scan_generation_acceptance import (
    run_arkit_scan_generation_acceptance,
)
from myth_forge_api.providers.three_d import LocalThreeDProvider, ThreeDGenerationRequest


class RecordingThreeDProvider:
    provider_name = "recording"

    def __init__(self) -> None:
        self.requests: list[ThreeDGenerationRequest] = []
        self.local_provider = LocalThreeDProvider()

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        self.requests.append(request)
        return self.local_provider.generate_game_asset(request)


def test_arkit_scan_generation_acceptance_runs_scan_asset_and_reference_images(
    tmp_path,
) -> None:
    result = run_arkit_scan_generation_acceptance(capture_storage_dir=tmp_path / "captures")

    report_text = json.dumps(result.report)
    assert result.exit_code == 0
    assert result.report["kind"] == "arkit_scan_generation_acceptance_report"
    assert result.report["status"] == "succeeded"
    assert result.report["summary"] == {"passed": 6, "failed": 0}
    assert result.report["capture"]["capture_mode"] == "arkit_scan"
    assert result.report["capture"]["capture_media_count"] == 3
    assert result.report["capture"]["reference_image_count"] == 2
    assert result.report["capture"]["scan_asset_count"] == 1
    assert result.report["generation_request"]["source_image_count"] == 2
    assert result.report["generation_request"]["source_asset_count"] == 1
    assert result.report["generation_request"]["source_image_content_types"] == [
        "image/jpeg",
        "image/png",
    ]
    assert result.report["generation_request"]["source_asset_content_types"] == [
        "model/gltf-binary"
    ]
    assert result.report["generation_provenance"]["input_mode"] == "multi_image"
    assert result.report["generation_provenance"]["source_image_count"] == 2
    assert result.report["generation_provenance"]["selected_source_image_count"] == 2
    assert result.report["generation_provenance"]["source_asset_count"] == 1
    assert result.report["generation_provenance"]["raw_sources_included"] is False
    assert result.report["scene_loadable_variant"] is True
    assert result.report["safety"]["raw_media_in_report"] is False
    assert result.report["safety"]["local_paths_in_report"] is False
    assert result.report["safety"]["provider_secrets_in_report"] is False
    assert "data:image" not in report_text
    assert "local-capture://" not in report_text
    assert str(tmp_path) not in report_text


def test_arkit_scan_generation_acceptance_passes_sources_to_provider(tmp_path) -> None:
    provider = RecordingThreeDProvider()

    result = run_arkit_scan_generation_acceptance(
        capture_storage_dir=tmp_path / "captures",
        three_d_provider=provider,
    )

    assert result.exit_code == 0
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert len(request.source_images) == 2
    assert len(request.source_assets) == 1
    assert [image.content_type for image in request.source_images] == [
        "image/jpeg",
        "image/png",
    ]
    assert all(
        image.data_uri.startswith(f"data:{image.content_type};base64,")
        for image in request.source_images
    )
    assert [asset.content_type for asset in request.source_assets] == [
        "model/gltf-binary"
    ]


class FailingThreeDProvider:
    provider_name = "failing"

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        raise RuntimeError(
            "failed data:image/png;base64,AAAA "
            "local-capture://cap_0123456789abcdef/media_0.png "
            "/tmp/personal-myth-forge/private.png "
            "Authorization=Bearer provider-secret raw=private"
        )


def test_arkit_scan_generation_acceptance_sanitizes_failure_report(tmp_path) -> None:
    result = run_arkit_scan_generation_acceptance(
        capture_storage_dir=tmp_path / "captures",
        three_d_provider=FailingThreeDProvider(),
    )

    report_text = json.dumps(result.report)
    assert result.exit_code == 1
    assert result.report["kind"] == "arkit_scan_generation_acceptance_report"
    assert result.report["status"] == "failed"
    assert "data:image" not in report_text
    assert "local-capture://" not in report_text
    assert "provider-secret" not in report_text
    assert "Authorization" not in report_text
    assert str(tmp_path) not in report_text
