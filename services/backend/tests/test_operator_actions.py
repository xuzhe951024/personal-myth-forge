from myth_forge_api.operator_actions import normalize_operator_action


def test_normalizes_provider_handoff_cli_action_to_make_target() -> None:
    action = (
        "rerun provider handoff readiness: "
        "cd services/backend && uv run python -m myth_forge_api.cli "
        "provider-handoff --require-core-real --output .local/provider-handoff.json"
    )

    assert normalize_operator_action(action) == (
        "rerun provider handoff readiness: make provider-handoff"
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
