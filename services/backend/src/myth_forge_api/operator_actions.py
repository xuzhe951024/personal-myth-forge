from __future__ import annotations

LEGACY_FINAL_RESOURCE_COPY_MARKERS = (
    "services/backend/final-resources.env.example",
    "services/backend/.local/final-resources.env",
)
NORMALIZED_FINAL_RESOURCE_INIT_ACTION = "run make final-resource-init"
FINAL_RESOURCE_APPLY_ACTION = "make final-apply-resources"
FINAL_RESOURCE_APPLY_ACTION_ROOTS = (
    "make final-apply-resources",
    "run make final-apply-resources",
)
PROVIDER_SELECTION_ACTION_ROOTS = (
    "set THREE_D_PROVIDER=meshy",
    "set NPC_PROVIDER=openai",
)
MOBILE_DEPLOY_PREFLIGHT_COMMAND = "make mobile-deploy-preflight"
DEPLOYMENT_TEAM_ACTION = "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig"
PRODUCT_BUNDLE_IDENTIFIER_ACTION = (
    "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig"
)
BACKEND_BASE_URL_ACTION = "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
MOBILE_WRITE_DEPLOY_CONFIG_AUTO_ACTION = (
    "DEVELOPMENT_TEAM=YOUR_TEAM_ID make mobile-write-deploy-config-auto"
)
BACKEND_DEVICE_DEMO_ACTION = (
    "start backend-device-demo before device checks: make backend-device-demo"
)
BACKEND_DEVICE_DEMO_VALIDATED_ACTION = (
    f"{BACKEND_DEVICE_DEMO_ACTION}; rerun {MOBILE_DEPLOY_PREFLIGHT_COMMAND}"
)
MAKE_TARGET_ACTION_REPLACEMENTS = {
    "rerun provider handoff readiness: make provider-handoff": (
        "make provider-handoff"
    ),
    "run make live-provider-evidence after configured provider evidence files are refreshed": (
        "make live-provider-evidence"
    ),
    "run make live-provider-evidence to refresh live provider evidence after cost consent": (
        "make live-provider-evidence"
    ),
    "run make final-acceptance-configured only after live provider cost review "
    "and --allow-live-provider-calls consent": (
        "approve live provider cost review before make final-acceptance-configured; "
        "--allow-live-provider-calls consent required"
    ),
    "run make final-resource-requirements after filling resources": (
        "make final-resource-requirements"
    ),
    "run make final-configured-preflight": "make final-configured-preflight",
    "run make final-demo-launch-configured": "make final-demo-launch-configured",
    "run make final-demo-launch-local": "make final-demo-launch-local",
    "run make final-handoff-index": "make final-handoff-index",
    "run make ios-deploy-runbook-local": "make ios-deploy-runbook-local",
    "run make ios-device-launch-rehearsal": "make ios-device-launch-rehearsal",
    "rerun make ios-device-launch-rehearsal to regenerate "
    "services/backend/.local/ios-device-launch-rehearsal.json for the current "
    "product sources": "make ios-device-launch-rehearsal",
    "run make mobile-deploy-preflight after backend is running": (
        BACKEND_DEVICE_DEMO_VALIDATED_ACTION
    ),
}
XCODE_BUILD_GATE_ACTION = (
    "accept the Xcode license outside Codex, then rerun "
    "make mobile-xcode-build-evidence"
)
GENERIC_ACTION_REPLACEMENTS = {
    "resolve Xcode build gate outside the app": XCODE_BUILD_GATE_ACTION,
}
PROVIDER_HANDOFF_CLI_MARKERS = ("myth_forge_api.cli provider-handoff",)
FINAL_DEMO_LAUNCH_CONFIGURED_CLI_MARKERS = (
    "myth_forge_api.cli final-demo-launch",
    "--mode configured",
)
FINAL_DEMO_LAUNCH_LOCAL_CLI_MARKERS = (
    "myth_forge_api.cli final-demo-launch",
    "--mode local",
)
FINAL_RESOURCE_VALIDATION_ACTION_ROOTS = (
    "provide MESHY_API_KEY in final-resources.env",
    "provide OPENAI_API_KEY in final-resources.env",
    "provide TREATSTOCK_API_KEY in final-resources.env",
    "provide SCULPTEO_API_KEY in final-resources.env",
    "provide DEVELOPMENT_TEAM in final-resources.env",
    "provide PRODUCT_BUNDLE_IDENTIFIER in final-resources.env",
    "provide PMF_BACKEND_BASE_URL in final-resources.env",
)
FINAL_RESOURCE_FILL_TARGET = "services/backend/.local/final-resources.env"
FINAL_RESOURCES_PREFLIGHT_COMMAND = "make final-resources-preflight"
UNBLOCK_ACTION_REPLACEMENTS = {
    "unblock final_resource_fill_guide after MESHY_API_KEY": (
        "provide MESHY_API_KEY in final-resources.env; "
        f"rerun {FINAL_RESOURCES_PREFLIGHT_COMMAND}"
    ),
    "unblock final_resource_fill_guide before configured evidence bundle": (
        "provide MESHY_API_KEY in final-resources.env; "
        f"rerun {FINAL_RESOURCES_PREFLIGHT_COMMAND}"
    ),
    "unblock provider_handoff before configured evidence bundle": (
        "make provider-handoff"
    ),
    "unblock final_resource_apply_preview after final_resource_fill_guide": (
        "make final-resource-apply-preview"
    ),
    "unblock final_apply_resources after final_resource_apply_preview": (
        FINAL_RESOURCE_APPLY_ACTION
    ),
    "unblock final_configured_preflight after final_apply_resources": (
        "make final-configured-preflight"
    ),
    "unblock provider_handoff after final_configured_preflight": (
        "make provider-handoff"
    ),
    "unblock three_d_evaluation_configured after final_configured_preflight": (
        "make backend-evaluate-3d-configured"
    ),
    "unblock npc_evaluation_configured after final_configured_preflight": (
        "make backend-evaluate-npc-configured"
    ),
    "unblock final_acceptance_configured after final_configured_preflight": (
        "make final-acceptance-configured"
    ),
    "unblock final_demo_launch_configured after final_configured_preflight": (
        "make final-demo-launch-configured"
    ),
    "unblock live_provider_evidence after final_configured_preflight": (
        "make live-provider-evidence"
    ),
}
IOS_DEPLOY_CONFIG_ACTION = "provide iOS deploy config in Deployment.local.xcconfig"
IOS_DEPLOY_CONFIG_VALIDATED_ACTION = (
    f"{IOS_DEPLOY_CONFIG_ACTION}; rerun {MOBILE_DEPLOY_PREFLIGHT_COMMAND}"
)
LEGACY_BACKEND_DEVICE_DEMO_ACTIONS = (
    "start backend-device-demo",
    "start backend-device-demo and rerun mobile deploy preflight",
    "continue with make backend-device-demo",
)
LEGACY_IOS_DEPLOY_CONFIG_ACTIONS = (
    "provide iOS deploy config",
    "provide iOS deploy config and rerun mobile deploy preflight",
)
MOBILE_DEPLOY_VALIDATION_ACTION_ROOTS = (
    BACKEND_DEVICE_DEMO_ACTION,
    IOS_DEPLOY_CONFIG_ACTION,
    DEPLOYMENT_TEAM_ACTION,
    PRODUCT_BUNDLE_IDENTIFIER_ACTION,
    "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig",
    BACKEND_BASE_URL_ACTION,
    MOBILE_WRITE_DEPLOY_CONFIG_AUTO_ACTION,
    "set PMF_FINAL_LAUNCH_MODE to local or configured",
)


def normalize_operator_action(action: str) -> str:
    normalized = action.strip()
    command_part, detail_suffix = _split_detail_suffix(normalized)
    mobile_preflight_detail_action = _normalize_mobile_preflight_detail_action(
        command_part
    )
    if mobile_preflight_detail_action is not None:
        return f"{mobile_preflight_detail_action}{detail_suffix}"
    legacy_action = _normalize_legacy_action(command_part)
    if legacy_action is not None:
        return f"{legacy_action}{detail_suffix}"
    unblock_action = _normalize_unblock_action(command_part)
    if unblock_action is not None:
        return f"{unblock_action}{detail_suffix}"
    final_resource_fill_action = _normalize_final_resource_fill_action(command_part)
    if final_resource_fill_action is not None:
        return f"{final_resource_fill_action}{detail_suffix}"
    generic_action = _normalize_generic_action(command_part)
    if generic_action is not None:
        return f"{generic_action}{detail_suffix}"
    make_target_action = _normalize_make_target_action(command_part)
    if make_target_action is not None:
        return f"{make_target_action}{detail_suffix}"
    mobile_validated_action = _add_mobile_deploy_validation_to_command(command_part)
    if mobile_validated_action != command_part:
        return f"{mobile_validated_action}{detail_suffix}"
    apply_root = command_part.split("; rerun ", 1)[0].strip()
    if apply_root in FINAL_RESOURCE_APPLY_ACTION_ROOTS:
        return f"{FINAL_RESOURCE_APPLY_ACTION}{detail_suffix}"
    if command_part in PROVIDER_SELECTION_ACTION_ROOTS:
        return f"{FINAL_RESOURCE_APPLY_ACTION}{detail_suffix}"
    if all(marker in command_part for marker in LEGACY_FINAL_RESOURCE_COPY_MARKERS):
        return f"{NORMALIZED_FINAL_RESOURCE_INIT_ACTION}{detail_suffix}"
    if command_part.endswith(f": {NORMALIZED_FINAL_RESOURCE_INIT_ACTION}"):
        return f"{NORMALIZED_FINAL_RESOURCE_INIT_ACTION}{detail_suffix}"
    command = _normalized_command(command_part)
    if command is not None:
        replaced = _replace_action_command(command_part, command)
        make_target_action = _normalize_make_target_action(replaced)
        if make_target_action is not None:
            return f"{make_target_action}{detail_suffix}"
        return f"{replaced}{detail_suffix}"
    return f"{command_part}{detail_suffix}"


def _normalize_make_target_action(action: str) -> str | None:
    if action in MAKE_TARGET_ACTION_REPLACEMENTS:
        return MAKE_TARGET_ACTION_REPLACEMENTS[action]
    for verbose, replacement in MAKE_TARGET_ACTION_REPLACEMENTS.items():
        suffix = f": {verbose}"
        if action.endswith(suffix):
            prefix = action[: -len(suffix)]
            return f"{prefix}: {replacement}"
    return None


def _normalize_mobile_preflight_detail_action(action: str) -> str | None:
    marker = "mobile_deploy_preflight_evidence: "
    if marker not in action:
        return None
    prefix, _separator, detail = action.partition(marker)
    stripped_detail = detail.strip()
    if not stripped_detail:
        return None
    if f"rerun {MOBILE_DEPLOY_PREFLIGHT_COMMAND}" in stripped_detail:
        return None
    root: str | None = None
    if "DEVELOPMENT_TEAM" in stripped_detail:
        root = DEPLOYMENT_TEAM_ACTION
    elif "PRODUCT_BUNDLE_IDENTIFIER" in stripped_detail:
        root = PRODUCT_BUNDLE_IDENTIFIER_ACTION
    elif (
        "PMF_BACKEND_BASE_URL" in stripped_detail
        or "iPhone-reachable" in stripped_detail
    ):
        root = BACKEND_BASE_URL_ACTION
    if root is None:
        return None
    command = _add_mobile_deploy_validation_to_command(root)
    return f"{prefix}{marker}{command} | {stripped_detail}"


def _normalize_unblock_action(action: str) -> str | None:
    if action in UNBLOCK_ACTION_REPLACEMENTS:
        return UNBLOCK_ACTION_REPLACEMENTS[action]
    for vague, replacement in UNBLOCK_ACTION_REPLACEMENTS.items():
        suffix = f": {vague}"
        if action.endswith(suffix):
            prefix = action[: -len(suffix)]
            return f"{prefix}: {replacement}"
    return None


def _normalize_final_resource_fill_action(action: str) -> str | None:
    command_root = action.split("; rerun ", 1)[0].strip()
    prefix = "fill "
    suffix = f" in {FINAL_RESOURCE_FILL_TARGET}"
    if not command_root.startswith(prefix) or not command_root.endswith(suffix):
        return None
    resource_id = command_root[len(prefix) : -len(suffix)].strip()
    canonical = f"provide {resource_id} in final-resources.env"
    if canonical not in FINAL_RESOURCE_VALIDATION_ACTION_ROOTS:
        return None
    return add_final_resource_validation_command(canonical)


def _normalize_generic_action(action: str) -> str | None:
    if action in GENERIC_ACTION_REPLACEMENTS:
        return GENERIC_ACTION_REPLACEMENTS[action]
    for vague, replacement in GENERIC_ACTION_REPLACEMENTS.items():
        suffix = f": {vague}"
        if action.endswith(suffix):
            prefix = action[: -len(suffix)]
            return f"{prefix}: {replacement}"
    return None


def _normalize_legacy_action(action: str) -> str | None:
    legacy_actions = {
        **dict.fromkeys(
            LEGACY_BACKEND_DEVICE_DEMO_ACTIONS,
            BACKEND_DEVICE_DEMO_VALIDATED_ACTION,
        ),
        **dict.fromkeys(
            LEGACY_IOS_DEPLOY_CONFIG_ACTIONS,
            IOS_DEPLOY_CONFIG_VALIDATED_ACTION,
        ),
    }
    if action in legacy_actions:
        return legacy_actions[action]
    for legacy, replacement in legacy_actions.items():
        suffix = f": {legacy}"
        if action.endswith(suffix):
            prefix = action[: -len(suffix)]
            return f"{prefix}: {replacement}"
    return None


def add_final_resource_validation_command(action: str) -> str:
    normalized = action.strip()
    root = normalized.split("; rerun ", 1)[0].strip()
    if root.endswith(FINAL_RESOURCE_VALIDATION_ACTION_ROOTS):
        return f"{root}; rerun {FINAL_RESOURCES_PREFLIGHT_COMMAND}"
    if "; rerun " in normalized:
        return normalized
    return normalized


def add_mobile_deploy_validation_command(action: str) -> str:
    normalized = action.strip()
    command_part, detail_suffix = _split_detail_suffix(normalized)
    return f"{_add_mobile_deploy_validation_to_command(command_part)}{detail_suffix}"


def _add_mobile_deploy_validation_to_command(action: str) -> str:
    command_part = action.strip()
    if "; rerun " in command_part:
        return command_part
    if command_part.endswith(MOBILE_DEPLOY_VALIDATION_ACTION_ROOTS):
        return f"{command_part}; rerun {MOBILE_DEPLOY_PREFLIGHT_COMMAND}"
    return command_part


def _split_detail_suffix(action: str) -> tuple[str, str]:
    command, separator, detail = action.partition(" | ")
    if not separator:
        return action, ""
    return command.strip(), f"{separator}{detail}"


def _normalized_command(action: str) -> str | None:
    if all(marker in action for marker in PROVIDER_HANDOFF_CLI_MARKERS):
        return "make provider-handoff"
    if all(marker in action for marker in FINAL_DEMO_LAUNCH_CONFIGURED_CLI_MARKERS):
        return "make final-demo-launch-configured"
    if all(marker in action for marker in FINAL_DEMO_LAUNCH_LOCAL_CLI_MARKERS):
        return "make final-demo-launch-local"
    return None


def _replace_action_command(action: str, command: str) -> str:
    if ": run " in action:
        prefix, _separator, _raw_command = action.rpartition(": run ")
        return f"{prefix}: run {command}"
    if action.startswith("run "):
        return f"run {command}"
    if ": " in action:
        prefix, _separator, _raw_command = action.rpartition(": ")
        return f"{prefix}: {command}"
    return command
