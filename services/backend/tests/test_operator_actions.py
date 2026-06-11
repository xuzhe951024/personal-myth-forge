import myth_forge_api.operator_actions as operator_actions
from myth_forge_api.operator_actions import normalize_operator_action


def test_adds_mobile_deploy_validation_to_known_ios_config_actions() -> None:
    assert operator_actions.add_mobile_deploy_validation_command(
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig"
    ) == (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert operator_actions.add_mobile_deploy_validation_command(
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig"
    ) == (
        "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert operator_actions.add_mobile_deploy_validation_command(
        "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig"
    ) == (
        "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight"
    )
    assert operator_actions.add_mobile_deploy_validation_command(
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
    ) == (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    )
    assert operator_actions.add_mobile_deploy_validation_command(
        "set PMF_FINAL_LAUNCH_MODE to local or configured"
    ) == (
        "set PMF_FINAL_LAUNCH_MODE to local or configured; "
        "rerun make mobile-deploy-preflight"
    )


def test_mobile_deploy_validation_preserves_existing_rerun_command() -> None:
    action = (
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make ios-device-launch-rehearsal"
    )

    assert operator_actions.add_mobile_deploy_validation_command(action) == action


def test_normalizes_backend_device_demo_action_to_validated_make_target() -> None:
    expected = (
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight"
    )

    assert (
        normalize_operator_action(
            "start backend-device-demo and rerun mobile deploy preflight"
        )
        == expected
    )
    assert (
        operator_actions.add_mobile_deploy_validation_command(
            "start backend-device-demo before device checks: make backend-device-demo"
        )
        == expected
    )


def test_normalizes_prefixed_backend_device_demo_action() -> None:
    assert normalize_operator_action(
        "ios_device_launch_certificate: start backend-device-demo"
    ) == (
        "ios_device_launch_certificate: start backend-device-demo before device "
        "checks: make backend-device-demo; rerun make mobile-deploy-preflight"
    )


def test_normalizes_detail_suffixed_backend_device_demo_action() -> None:
    action = (
        "start backend-device-demo before device checks: make backend-device-demo "
        "| PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    expected = (
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight | PMF_BACKEND_BASE_URL must be "
        "iPhone-reachable"
    )

    assert normalize_operator_action(action) == expected
    assert operator_actions.add_mobile_deploy_validation_command(action) == expected


def test_normalizes_prefixed_ios_deploy_config_action() -> None:
    expected = (
        "ios_device_launch_certificate: provide iOS deploy config in "
        "Deployment.local.xcconfig; rerun make mobile-deploy-preflight"
    )

    assert (
        normalize_operator_action("ios_device_launch_certificate: provide iOS deploy config")
        == expected
    )
    assert (
        normalize_operator_action(
            "ios_device_launch_certificate: provide iOS deploy config and rerun "
            "mobile deploy preflight"
        )
        == expected
    )


def test_normalizes_provider_handoff_cli_action_to_make_target() -> None:
    action = (
        "rerun provider handoff readiness: "
        "cd services/backend && uv run python -m myth_forge_api.cli "
        "provider-handoff --require-core-real --output .local/provider-handoff.json"
    )

    assert normalize_operator_action(action) == "make provider-handoff"


def test_normalizes_verbose_provider_evidence_actions_to_make_targets() -> None:
    assert normalize_operator_action(
        "rerun provider handoff readiness: make provider-handoff"
    ) == "make provider-handoff"
    assert normalize_operator_action(
        "run make live-provider-evidence after configured provider evidence files "
        "are refreshed"
    ) == "make live-provider-evidence"
    assert normalize_operator_action(
        "run make live-provider-evidence to refresh live provider evidence after "
        "cost consent | configured evidence stale"
    ) == "make live-provider-evidence | configured evidence stale"


def test_normalizes_xcode_gate_actions_to_evidence_command() -> None:
    expected = (
        "accept the Xcode license outside Codex, then rerun "
        "make mobile-xcode-build-evidence"
    )

    assert normalize_operator_action("resolve Xcode build gate outside the app") == (
        expected
    )
    assert normalize_operator_action(
        "final_rehearsal_local: final_acceptance_local: resolve Xcode build gate "
        "outside the app"
    ) == f"final_rehearsal_local: final_acceptance_local: {expected}"
    assert normalize_operator_action(
        "resolve Xcode build gate outside the app | xcodebuild license blocked"
    ) == f"{expected} | xcodebuild license blocked"


def test_normalizes_final_resource_requirements_action_to_make_target() -> None:
    assert normalize_operator_action(
        "run make final-resource-requirements after filling resources"
    ) == "make final-resource-requirements"
    assert normalize_operator_action(
        "run make final-resource-requirements after filling resources | resources ready"
    ) == "make final-resource-requirements | resources ready"


def test_normalizes_final_handoff_make_wrappers_to_make_targets() -> None:
    assert normalize_operator_action(
        "run make final-configured-preflight"
    ) == "make final-configured-preflight"
    assert normalize_operator_action(
        "final_handoff_index: run make final-demo-launch-configured"
    ) == "final_handoff_index: make final-demo-launch-configured"
    assert normalize_operator_action(
        "ios_device_launch_certificate: run make final-handoff-index"
    ) == "ios_device_launch_certificate: make final-handoff-index"
    assert normalize_operator_action(
        "ios_device_launch_certificate: run make ios-deploy-runbook-local | stale"
    ) == "ios_device_launch_certificate: make ios-deploy-runbook-local | stale"


def test_normalizes_mobile_deploy_after_backend_action_to_device_handoff() -> None:
    expected = (
        "start backend-device-demo before device checks: make backend-device-demo; "
        "rerun make mobile-deploy-preflight"
    )

    assert (
        normalize_operator_action(
            "run make mobile-deploy-preflight after backend is running"
        )
        == expected
    )
    assert (
        normalize_operator_action(
            "final_handoff_index: run make mobile-deploy-preflight after backend "
            "is running"
        )
        == f"final_handoff_index: {expected}"
    )
    assert (
        normalize_operator_action(
            "ios_device_launch_certificate: run make mobile-deploy-preflight after "
            "backend is running | backend missing"
        )
        == f"ios_device_launch_certificate: {expected} | backend missing"
    )


def test_normalizes_vague_unblock_actions_to_concrete_commands() -> None:
    assert normalize_operator_action(
        "unblock final_resource_fill_guide after MESHY_API_KEY"
    ) == (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )
    assert normalize_operator_action(
        "final_showcase_readiness: unblock provider_handoff before configured "
        "evidence bundle"
    ) == "final_showcase_readiness: make provider-handoff"


def test_normalizes_resource_apply_unblock_actions_to_concrete_commands() -> None:
    assert normalize_operator_action(
        "unblock final_resource_apply_preview after final_resource_fill_guide"
    ) == "make final-resource-apply-preview"
    assert normalize_operator_action(
        "final_showcase_readiness: unblock final_apply_resources after "
        "final_resource_apply_preview"
    ) == (
        "final_showcase_readiness: run make final-apply-resources to apply the "
        "filled resource bundle"
    )


def test_normalizes_provider_selection_actions_to_final_apply() -> None:
    assert normalize_operator_action("set THREE_D_PROVIDER=meshy") == (
        "run make final-apply-resources to apply the filled resource bundle"
    )
    assert normalize_operator_action("set NPC_PROVIDER=openai") == (
        "run make final-apply-resources to apply the filled resource bundle"
    )


def test_normalizes_final_apply_actions_to_explicit_handoff() -> None:
    expected = "run make final-apply-resources to apply the filled resource bundle"

    assert normalize_operator_action("make final-apply-resources") == expected
    assert (
        normalize_operator_action(
            "make final-apply-resources; rerun make final-resources-preflight"
        )
        == expected
    )
    assert normalize_operator_action("run make final-apply-resources") == expected


def test_normalizes_configured_final_demo_launch_cli_action_to_make_target() -> None:
    action = (
        "final_handoff_index: run cd services/backend && uv run python -m "
        "myth_forge_api.cli final-demo-launch --mode configured --repo-root [repo-root] "
        "--output .local/final-demo-launch-configured.json"
    )

    assert normalize_operator_action(action) == (
        "final_handoff_index: make final-demo-launch-configured"
    )


def test_normalizes_local_final_demo_launch_cli_action_to_make_target() -> None:
    action = (
        "ios_device_launch_certificate: run cd services/backend && uv run python -m "
        "myth_forge_api.cli final-demo-launch --mode local --repo-root ../.. "
        "--output .local/final-demo-launch-local.json"
    )

    assert normalize_operator_action(action) == (
        "ios_device_launch_certificate: make final-demo-launch-local"
    )
