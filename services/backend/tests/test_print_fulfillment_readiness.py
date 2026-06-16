import json
from pathlib import Path

from myth_forge_api.config import Settings
from myth_forge_api.print_fulfillment_readiness import (
    build_print_fulfillment_readiness_report,
)
from myth_forge_api.visual_regression import DEFAULT_VISUAL_ARTIFACTS


def test_print_fulfillment_readiness_blocks_missing_local_evidence(tmp_path: Path) -> None:
    result = build_print_fulfillment_readiness_report(
        settings=Settings(),
        repo_root=tmp_path,
    )

    assert result.exit_code == 2
    assert result.report["kind"] == "print_fulfillment_readiness_report"
    assert result.report["status"] == "blocked"
    assert result.report["summary"]["blocked"] >= 1
    assert result.report["first_blocker"]["id"] == "ios_print_fulfillment_source"
    assert result.report["checks_by_id"]["print_quote_acceptance"]["status"] == "ready"
    assert result.report["checks_by_id"]["ios_print_fulfillment_source"]["status"] == "blocked"
    assert result.report["safety"]["commands_run"] is False
    assert result.report["safety"]["live_provider_calls"] is False
    assert result.report["safety"]["payment_links_in_report"] is False


def test_print_fulfillment_readiness_ready_for_local_print_asset_without_provider_quote(
    tmp_path: Path,
) -> None:
    _write_local_print_readiness_fixture(tmp_path)

    result = build_print_fulfillment_readiness_report(
        settings=Settings(print_provider="local"),
        repo_root=tmp_path,
    )
    rows = result.report["checks_by_id"]

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert rows["print_quote_acceptance"]["status"] == "ready"
    assert rows["ios_print_fulfillment_source"]["status"] == "ready"
    assert rows["visual_print_receipt"]["status"] == "ready"
    assert rows["print_resource_handoff"]["status"] == "ready"
    assert rows["configured_treatstock_quote_request"]["status"] == "deferred"
    assert rows["configured_treatstock_quote_request"]["classification"] == (
        "provider_quote_deferred_for_local_print_asset"
    )
    assert rows["configured_treatstock_quote"]["status"] == "deferred"
    assert rows["configured_treatstock_quote"]["classification"] == (
        "provider_quote_deferred_for_local_print_asset"
    )
    assert result.report["summary"]["deferred"] == 2
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["operator_actions"] == []
    assert "print-fulfillment-readiness" in " ".join(result.report["commands"])
    assert "print-quote-configured" in " ".join(result.report["commands"])


def test_print_fulfillment_readiness_points_to_local_demo_session_before_auto_request(
    tmp_path: Path,
) -> None:
    _write_local_print_readiness_fixture(tmp_path, print_provider="treatstock")

    result = build_print_fulfillment_readiness_report(
        settings=Settings(
            print_provider="treatstock",
            treatstock_api_key="sk-treatstock-secret",
        ),
        repo_root=tmp_path,
    )
    rows = result.report["checks_by_id"]

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert rows["configured_treatstock_quote_request"]["status"] == "blocked"
    assert rows["configured_treatstock_quote_request"]["classification"] == (
        "missing_local_demo_session_for_print_quote_request"
    )
    assert result.report["first_blocker"]["id"] == "configured_treatstock_quote_request"
    assert result.report["first_blocker"]["command"] == "make final-demo-launch-local"
    expected_command = "make final-demo-launch-local; rerun make print-fulfillment-readiness"
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "command": expected_command,
        "source": "first_blocker",
        "validation_command": "make print-fulfillment-readiness",
        "requires_cost_consent": False,
    }
    assert result.report["operator_actions"][0] == expected_command


def test_print_fulfillment_readiness_points_to_backend_url_before_auto_request(
    tmp_path: Path,
) -> None:
    _write_local_print_readiness_fixture(
        tmp_path,
        print_provider="treatstock",
        backend_base_url="http://127.0.0.1:8080",
    )
    _write_final_demo_launch_local_session(tmp_path, session_id="myth_showcase123")

    result = build_print_fulfillment_readiness_report(
        settings=Settings(
            print_provider="treatstock",
            treatstock_api_key="sk-treatstock-secret",
        ),
        repo_root=tmp_path,
    )
    rows = result.report["checks_by_id"]

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert rows["configured_treatstock_quote_request"]["status"] == "blocked"
    assert rows["configured_treatstock_quote_request"]["classification"] == (
        "missing_iphone_reachable_backend_url_for_print_quote_request"
    )
    assert result.report["first_blocker"]["id"] == "configured_treatstock_quote_request"
    expected_command = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID PMF_BACKEND_BASE_URL=auto "
        "make mobile-write-deploy-config-auto"
    )
    assert result.report["first_blocker"]["command"] == expected_command
    expected_next_command = (
        f"{expected_command}; rerun make print-fulfillment-readiness"
    )
    assert result.report["next_action"]["command"] == expected_next_command
    assert result.report["operator_actions"][0] == expected_next_command


def test_print_fulfillment_readiness_suggests_local_served_quote_request_uris(
    tmp_path: Path,
) -> None:
    _write_local_print_readiness_fixture(tmp_path, print_provider="treatstock")
    _write_final_demo_launch_local_session(tmp_path, session_id="myth_showcase123")

    result = build_print_fulfillment_readiness_report(
        settings=Settings(
            print_provider="treatstock",
            treatstock_api_key="sk-treatstock-secret",
        ),
        repo_root=tmp_path,
    )

    assert result.report["first_blocker"]["id"] == "configured_treatstock_quote_request"
    expected_command = (
        "PRINT_SOURCE_ASSET_URI=http://192.168.1.10:8080/v1/generated-assets/"
        "myth_showcase123/game.glb "
        "PRINT_CANDIDATE_URI=http://192.168.1.10:8080/v1/print-candidates/"
        "myth_showcase123/print.3mf "
        "make print-quote-request-configured"
    )
    expected_next_command = (
        f"{expected_command}; rerun make print-fulfillment-readiness"
    )
    assert result.report["next_action"]["command"] == expected_next_command
    assert result.report["operator_actions"][0] == expected_next_command


def test_print_fulfillment_readiness_uses_top_level_final_demo_smoke_session(
    tmp_path: Path,
) -> None:
    _write_local_print_readiness_fixture(tmp_path, print_provider="treatstock")
    _write_json(
        tmp_path / "services/backend/.local/final-demo-launch-local.json",
        {
            "kind": "final_demo_launch_report",
            "status": "partial",
            "local_showcase_smoke": {
                "kind": "local_showcase_smoke_report",
                "status": "succeeded",
                "session": {"session_id": "myth_top_level123"},
            },
        },
    )

    result = build_print_fulfillment_readiness_report(
        settings=Settings(
            print_provider="treatstock",
            treatstock_api_key="sk-treatstock-secret",
        ),
        repo_root=tmp_path,
    )

    assert result.report["first_blocker"]["id"] == "configured_treatstock_quote_request"
    assert result.report["first_blocker"]["classification"] == (
        "missing_configured_treatstock_quote_request"
    )
    expected_command = (
        "PRINT_SOURCE_ASSET_URI=http://192.168.1.10:8080/v1/generated-assets/"
        "myth_top_level123/game.glb "
        "PRINT_CANDIDATE_URI=http://192.168.1.10:8080/v1/print-candidates/"
        "myth_top_level123/print.3mf "
        "make print-quote-request-configured"
    )
    assert result.report["next_action"]["command"] == (
        f"{expected_command}; rerun make print-fulfillment-readiness"
    )


def test_print_fulfillment_readiness_ready_with_configured_treatstock_quote(
    tmp_path: Path,
) -> None:
    _write_local_print_readiness_fixture(tmp_path, print_provider="treatstock")
    _write_configured_treatstock_quote(tmp_path)

    result = build_print_fulfillment_readiness_report(
        settings=Settings(
            print_provider="treatstock",
            treatstock_api_key="sk-treatstock-secret",
        ),
        repo_root=tmp_path,
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 0
    assert result.report["status"] == "ready"
    assert result.report["first_blocker"] is None
    assert result.report["next_action"] is None
    assert result.report["checks_by_id"]["configured_treatstock_quote"]["status"] == "ready"
    assert result.report["checks_by_id"]["configured_treatstock_quote"]["classification"] == (
        "draft_quote_requires_user_approval"
    )
    assert "sk-treatstock-secret" not in report_text
    assert "checkout.example" not in report_text
    assert "file://" not in report_text
    assert str(tmp_path) not in report_text


def test_print_fulfillment_readiness_blocks_unsafe_or_unapproved_treatstock_quote(
    tmp_path: Path,
) -> None:
    _write_local_print_readiness_fixture(tmp_path, print_provider="treatstock")
    _write_json(
        tmp_path / "services/backend/.local/print-quote-configured.json",
        {
            "kind": "print_quote",
            "provider": "treatstock",
            "status": "draft_quote",
            "currency": "USD",
            "estimated_price_cents": 2200,
            "checkout_url": "https://checkout.example/order?token=secret",
            "requires_user_approval": False,
            "approval_reason": "Bearer secret-token file:///tmp/private.3mf",
        },
    )

    result = build_print_fulfillment_readiness_report(
        settings=Settings(
            print_provider="treatstock",
            treatstock_api_key="sk-treatstock-secret",
        ),
        repo_root=tmp_path,
    )
    report_text = json.dumps(result.report)

    assert result.exit_code == 2
    assert result.report["status"] == "blocked"
    assert result.report["first_blocker"]["id"] == "configured_treatstock_quote"
    assert result.report["first_blocker"]["classification"] == "missing_user_approval_gate"
    expected_command = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
        "rerun make print-fulfillment-readiness"
    )
    assert result.report["next_action"] == {
        **result.report["first_blocker"],
        "command": expected_command,
        "source": "first_blocker",
        "validation_command": "make print-fulfillment-readiness",
        "requires_cost_consent": False,
    }
    assert "secret-token" not in report_text
    assert "checkout.example" not in report_text
    assert "file://" not in report_text


def _write_local_print_readiness_fixture(
    repo_root: Path,
    *,
    print_provider: str = "local",
    backend_base_url: str = "http://192.168.1.10:8080",
) -> None:
    _write_print_source_fixture(repo_root)
    _write_visual_regression_fixture(repo_root)
    _write_final_resources(repo_root, print_provider=print_provider)
    _write_deploy_config(repo_root, backend_base_url=backend_base_url)


def _write_print_source_fixture(repo_root: Path) -> None:
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCore/PrintFulfillmentReceipt.swift",
        "\n".join(
            [
                "PrintFulfillmentReceiptBuilder",
                "Checkout/payment links stay withheld",
                "canHandOffToProvider",
            ]
        ),
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/PrintFulfillmentReceiptView.swift",
        "Print Fulfillment",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/PrintQuoteReviewView.swift",
        "PrintFulfillmentReceiptView(receipt: fulfillmentReceipt) Approve Print Handoff",
    )
    _write_text(
        repo_root / "apps/mobile/ios/App/ForgeRootView.swift",
        "isPrintQuoteApproved PrintFulfillmentReceiptBuilder.build fulfillmentReceipt: printFulfillmentReceipt",
    )
    _write_text(
        repo_root / "apps/mobile/ios/PersonalMythForge.xcodeproj/project.pbxproj",
        "PrintFulfillmentReceiptView.swift",
    )
    _write_text(
        repo_root / "apps/mobile/ios/Sources/PersonalMythForgeMobileCoreContractTests/main.swift",
        "\n".join(
            [
                "testPrintFulfillmentReceiptRequiresApprovalBeforeHandoff",
                "testPrintFulfillmentReceiptBlocksAndRedactsUnsafeText",
            ]
        ),
    )


def _write_visual_regression_fixture(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/visual-regression-local.json",
        {
            "kind": "visual_regression_report",
            "status": "passed",
            "summary": {"passed": len(DEFAULT_VISUAL_ARTIFACTS), "failed": 0},
            "artifacts": [
                {
                    "id": artifact.id,
                    "status": "passed",
                    "html_path": artifact.html_path,
                    "png_path": artifact.png_path,
                }
                for artifact in DEFAULT_VISUAL_ARTIFACTS
            ],
        },
    )


def _write_final_resources(repo_root: Path, *, print_provider: str) -> None:
    lines = [
        "MESHY_API_KEY=sk-meshy-test",
        "OPENAI_API_KEY=sk-openai-test",
        f"PRINT_PROVIDER={print_provider}",
        "DEVELOPMENT_TEAM=TEAM12345",
        "PRODUCT_BUNDLE_IDENTIFIER=com.example.personalmythforge",
        "PMF_BACKEND_BASE_URL=http://192.168.1.10:8080",
        "PMF_FINAL_LAUNCH_MODE=local",
    ]
    if print_provider == "treatstock":
        lines.append("TREATSTOCK_API_KEY=sk-treatstock-secret")
    _write_text(
        repo_root / "services/backend/.local/final-resources.env",
        "\n".join(lines),
    )


def _write_deploy_config(
    repo_root: Path,
    *,
    backend_base_url: str = "http://192.168.1.10:8080",
) -> None:
    _write_text(
        repo_root / "apps/mobile/ios/Config/Deployment.local.xcconfig",
        "\n".join(
            [
                "DEVELOPMENT_TEAM = TEAM12345",
                "PRODUCT_BUNDLE_IDENTIFIER = com.example.personalmythforge",
                f"PMF_BACKEND_BASE_URL = {backend_base_url}",
            ]
        ),
    )


def _write_final_demo_launch_local_session(repo_root: Path, *, session_id: str) -> None:
    _write_json(
        repo_root / "services/backend/.local/final-demo-launch-local.json",
        {
            "kind": "final_demo_launch_report",
            "status": "partial",
            "source_reports": {
                "local_showcase_smoke": {
                    "kind": "local_showcase_smoke_report",
                    "status": "succeeded",
                    "session": {"session_id": session_id},
                }
            },
        },
    )


def _write_configured_treatstock_quote(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/print-quote-configured.json",
        {
            "kind": "print_quote",
            "provider": "treatstock",
            "status": "draft_quote",
            "currency": "USD",
            "estimated_price_cents": 2200,
            "estimated_production_days": 0,
            "estimated_shipping_days": 0,
            "checkout_url": "https://checkout.example/order?token=secret",
            "requires_user_approval": True,
            "approval_reason": "Treatstock quote requires review before checkout.",
        },
    )


def _write_configured_print_quote_request(repo_root: Path) -> None:
    _write_json(
        repo_root / "services/backend/.local/print-quote-request-configured.json",
        {
            "print_candidate": {
                "kind": "print_asset",
                "source_asset_uri": "https://assets.example/relic.glb",
                "provider": "local_stub",
                "format": "3mf",
                "uri": "https://assets.example/relic.3mf",
                "requires_user_approval": True,
                "approval_reason": "Review before configured quote.",
                "printability_notes": ["Watertight local handoff candidate."],
            },
            "quantity": 1,
            "material": "standard_resin",
            "finish": "matte",
            "ship_to_country": "US",
        },
    )


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
