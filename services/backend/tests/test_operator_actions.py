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


def test_adds_mobile_deploy_validation_to_writer_command() -> None:
    assert operator_actions.add_mobile_deploy_validation_command(
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
    ) == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )


def test_add_mobile_deploy_validation_command_dedupes_repeated_mobile_preflight() -> None:
    action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight; rerun make mobile-deploy-preflight"
    )
    expected = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )

    assert operator_actions.add_mobile_deploy_validation_command(action) == expected


def test_normalizes_run_prefixed_mobile_deploy_writer_command() -> None:
    assert normalize_operator_action(
        "run DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    ) == (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )


def test_prefers_project_local_ios_deploy_handoff_over_manual_team_action() -> None:
    actions = operator_actions.prefer_project_local_ios_deploy_handoff_actions(
        [
            (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                "make mobile-write-deploy-config-auto; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "provide DEVELOPMENT_TEAM in final-resources.env; "
                "rerun make final-resources-preflight"
            ),
        ]
    )

    assert actions == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "provide DEVELOPMENT_TEAM in final-resources.env; "
            "rerun make final-resources-preflight"
        ),
    ]


def test_preserves_manual_team_action_without_deploy_writer() -> None:
    actions = operator_actions.prefer_project_local_ios_deploy_handoff_actions(
        [
            (
                "provide DEVELOPMENT_TEAM in final-resources.env; "
                "rerun make final-resources-preflight"
            ),
            (
                "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            ),
        ]
    )

    assert actions == [
        (
            "provide DEVELOPMENT_TEAM in final-resources.env; "
            "rerun make final-resources-preflight"
        ),
        (
            "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
            "rerun make mobile-deploy-preflight"
        ),
    ]


def test_prefers_writer_over_generic_ios_deploy_config_action() -> None:
    actions = operator_actions.prefer_project_local_ios_deploy_handoff_actions(
        [
            (
                "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
                "make mobile-write-deploy-config-auto; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "provide iOS deploy config in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            ),
        ]
    )

    assert actions == [
        (
            "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
            "make mobile-write-deploy-config-auto; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
            "rerun make mobile-deploy-preflight"
        ),
    ]


def test_prefers_iphone_reachable_backend_url_over_generic_backend_config() -> None:
    actions = operator_actions.prefer_iphone_reachable_backend_url_handoff_actions(
        [
            (
                "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            )
        ]
    )

    assert actions == [
        (
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
            "rerun make mobile-deploy-preflight"
        )
    ]


def test_prefers_iphone_reachable_backend_url_collapses_duplicate_backend_actions() -> None:
    lan_backend_url_action = (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    )

    actions = operator_actions.prefer_iphone_reachable_backend_url_handoff_actions(
        [
            (
                "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
            lan_backend_url_action,
        ]
    )

    assert actions == [lan_backend_url_action]


def test_prefers_detail_writer_over_duplicate_bare_writer_action() -> None:
    bare_writer = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID "
        "make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    detailed_writer = (
        f"{bare_writer} | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )

    actions = operator_actions.prefer_project_local_ios_deploy_handoff_actions(
        [
            bare_writer,
            detailed_writer,
            (
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            ),
        ]
    )

    assert actions == [
        detailed_writer,
        (
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
            "rerun make mobile-deploy-preflight"
        ),
    ]


def test_preserves_generic_ios_deploy_config_action_without_writer() -> None:
    actions = operator_actions.prefer_project_local_ios_deploy_handoff_actions(
        [
            (
                "provide iOS deploy config in Deployment.local.xcconfig; "
                "rerun make mobile-deploy-preflight"
            ),
            (
                "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
                "rerun make mobile-deploy-preflight"
            ),
        ]
    )

    assert actions == [
        (
            "provide iOS deploy config in Deployment.local.xcconfig; "
            "rerun make mobile-deploy-preflight"
        ),
        (
            "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
            "rerun make mobile-deploy-preflight"
        ),
    ]


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


def test_normalizes_legacy_treatstock_quote_action_to_guarded_target() -> None:
    legacy_action = (
        "after explicit Treatstock cost consent, save a sanitized "
        "services/backend/.local/print-quote-configured.json from POST "
        "/v1/print-quotes"
    )
    guarded_action = "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured"

    assert normalize_operator_action(legacy_action) == guarded_action
    assert normalize_operator_action(
        f"{legacy_action}; rerun make print-fulfillment-readiness"
    ) == f"{guarded_action}; rerun make print-fulfillment-readiness"
    assert normalize_operator_action(
        f"final_demo_launch_local: {legacy_action}; rerun make print-fulfillment-readiness"
    ) == (
        "final_demo_launch_local: "
        f"{guarded_action}; rerun make print-fulfillment-readiness"
    )


def test_prefers_guarded_print_quote_action_over_legacy_variants() -> None:
    legacy_action = (
        "after explicit Treatstock cost consent, save a sanitized "
        "services/backend/.local/print-quote-configured.json from POST "
        "/v1/print-quotes; rerun make print-fulfillment-readiness"
    )
    guarded_action = (
        "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured; "
        "rerun make print-fulfillment-readiness"
    )

    actions = operator_actions.prefer_guarded_print_quote_handoff_actions(
        [
            "make provider-handoff; rerun make live-provider-evidence",
            legacy_action,
            guarded_action,
            f"final_demo_launch_local: {legacy_action}",
            f"final_demo_launch_local: {guarded_action}",
            "provide MESHY_API_KEY in final-resources.env",
        ]
    )

    assert actions == [
        "make provider-handoff; rerun make live-provider-evidence",
        guarded_action,
        "provide MESHY_API_KEY in final-resources.env",
    ]


def test_print_quote_preference_preserves_non_print_actions() -> None:
    stale_rehearsal_action = (
        "rerun make ios-device-launch-rehearsal to regenerate "
        "services/backend/.local/ios-device-launch-rehearsal.json for the current "
        "product sources"
    )

    actions = operator_actions.prefer_guarded_print_quote_handoff_actions(
        [stale_rehearsal_action]
    )

    assert actions == [stale_rehearsal_action]


def test_normalizes_configured_acceptance_cost_review_action() -> None:
    assert normalize_operator_action(
        "run make final-acceptance-configured only after live provider cost review "
        "and --allow-live-provider-calls consent"
    ) == (
        "approve live provider cost review before make final-acceptance-configured; "
        "--allow-live-provider-calls consent required"
    )


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
    ) == "make final-configured-preflight; rerun make configured-live-evidence-bundle"
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


def test_normalizes_mobile_preflight_evidence_details_to_deploy_handoff() -> None:
    writer_action = (
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight"
    )
    backend_url_action = (
        "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL; "
        "rerun make mobile-deploy-preflight"
    )

    assert normalize_operator_action(
        "final_rehearsal_local: mobile_deploy_preflight_evidence: "
        "Missing DEVELOPMENT_TEAM; PMF_BACKEND_BASE_URL must be iPhone-reachable"
    ) == (
        "final_rehearsal_local: mobile_deploy_preflight_evidence: "
        f"{writer_action} | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )
    assert normalize_operator_action(
        "mobile_deploy_preflight_evidence: PMF_BACKEND_BASE_URL must be "
        "iPhone-reachable"
    ) == (
        f"mobile_deploy_preflight_evidence: {backend_url_action} | "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )


def test_mobile_preflight_evidence_detail_normalization_is_idempotent() -> None:
    action = (
        "final_rehearsal_local: mobile_deploy_preflight_evidence: "
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; "
        "rerun make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
    )

    assert normalize_operator_action(action) == (
        "final_rehearsal_local: mobile_deploy_preflight_evidence: "
        "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto; "
        "rerun make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM; "
        "PMF_BACKEND_BASE_URL must be iPhone-reachable"
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


def test_normalizes_final_resource_fill_guide_action() -> None:
    assert normalize_operator_action(
        "fill MESHY_API_KEY in services/backend/.local/final-resources.env"
    ) == (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )


def test_normalizes_resource_apply_unblock_actions_to_concrete_commands() -> None:
    assert normalize_operator_action(
        "unblock final_resource_apply_preview after final_resource_fill_guide"
    ) == "make final-resource-apply-preview"
    assert normalize_operator_action(
        "final_showcase_readiness: unblock final_apply_resources after "
        "final_resource_apply_preview"
    ) == "final_showcase_readiness: make final-apply-resources"


def test_normalizes_configured_evidence_unblock_actions_to_make_targets() -> None:
    assert normalize_operator_action(
        "unblock final_resource_fill_guide before configured evidence bundle"
    ) == (
        "provide MESHY_API_KEY in final-resources.env; "
        "rerun make final-resources-preflight"
    )
    assert normalize_operator_action(
        "unblock final_configured_preflight after final_apply_resources"
    ) == "make final-configured-preflight"
    assert normalize_operator_action(
        "unblock provider_handoff after final_configured_preflight"
    ) == "make provider-handoff"
    assert normalize_operator_action(
        "unblock three_d_evaluation_configured after final_configured_preflight"
    ) == "make backend-evaluate-3d-configured"
    assert normalize_operator_action(
        "unblock npc_evaluation_configured after final_configured_preflight"
    ) == "make backend-evaluate-npc-configured"
    assert normalize_operator_action(
        "unblock final_acceptance_configured after final_configured_preflight"
    ) == "make final-acceptance-configured"
    assert normalize_operator_action(
        "unblock final_demo_launch_configured after final_configured_preflight"
    ) == "make final-demo-launch-configured"
    assert normalize_operator_action(
        "unblock live_provider_evidence after final_configured_preflight"
    ) == "make live-provider-evidence"


def test_normalizes_provider_selection_actions_to_final_apply() -> None:
    assert normalize_operator_action("set THREE_D_PROVIDER=meshy") == (
        "make final-apply-resources"
    )
    assert normalize_operator_action("set NPC_PROVIDER=openai") == (
        "make final-apply-resources"
    )


def test_normalizes_final_apply_actions_to_explicit_handoff() -> None:
    expected = "make final-apply-resources"

    assert normalize_operator_action("make final-apply-resources") == expected
    assert (
        normalize_operator_action(
            "make final-apply-resources; rerun make final-resources-preflight"
        )
        == expected
    )
    assert normalize_operator_action("run make final-apply-resources") == expected


def test_normalizes_ios_device_launch_rehearsal_run_make_action_to_make_target() -> None:
    action = (
        "run make ios-device-launch-rehearsal | "
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; rerun "
        "make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM"
    )

    assert normalize_operator_action(action) == (
        "make ios-device-launch-rehearsal | "
        "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig; rerun "
        "make mobile-deploy-preflight | Missing DEVELOPMENT_TEAM"
    )


def test_normalizes_ios_device_launch_rehearsal_rerun_action_to_make_target() -> None:
    assert normalize_operator_action(
        "rerun make ios-device-launch-rehearsal to regenerate "
        "services/backend/.local/ios-device-launch-rehearsal.json for the current "
        "product sources"
    ) == "make ios-device-launch-rehearsal"


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
