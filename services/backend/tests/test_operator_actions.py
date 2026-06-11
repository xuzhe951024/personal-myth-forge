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


def test_normalizes_provider_handoff_cli_action_to_make_target() -> None:
    action = (
        "rerun provider handoff readiness: "
        "cd services/backend && uv run python -m myth_forge_api.cli "
        "provider-handoff --require-core-real --output .local/provider-handoff.json"
    )

    assert normalize_operator_action(action) == (
        "rerun provider handoff readiness: make provider-handoff"
    )


def test_normalizes_provider_selection_actions_to_final_apply() -> None:
    assert normalize_operator_action("set THREE_D_PROVIDER=meshy") == (
        "run make final-apply-resources to apply the filled resource bundle"
    )
    assert normalize_operator_action("set NPC_PROVIDER=openai") == (
        "run make final-apply-resources to apply the filled resource bundle"
    )


def test_normalizes_configured_final_demo_launch_cli_action_to_make_target() -> None:
    action = (
        "final_handoff_index: run cd services/backend && uv run python -m "
        "myth_forge_api.cli final-demo-launch --mode configured --repo-root [repo-root] "
        "--output .local/final-demo-launch-configured.json"
    )

    assert normalize_operator_action(action) == (
        "final_handoff_index: run make final-demo-launch-configured"
    )


def test_normalizes_local_final_demo_launch_cli_action_to_make_target() -> None:
    action = (
        "ios_device_launch_certificate: run cd services/backend && uv run python -m "
        "myth_forge_api.cli final-demo-launch --mode local --repo-root ../.. "
        "--output .local/final-demo-launch-local.json"
    )

    assert normalize_operator_action(action) == (
        "ios_device_launch_certificate: run make final-demo-launch-local"
    )
