from __future__ import annotations

LEGACY_FINAL_RESOURCE_COPY_MARKERS = (
    "services/backend/final-resources.env.example",
    "services/backend/.local/final-resources.env",
)
NORMALIZED_FINAL_RESOURCE_INIT_ACTION = "run make final-resource-init"
FINAL_RESOURCE_APPLY_ACTION = (
    "run make final-apply-resources to apply the filled resource bundle"
)
FINAL_RESOURCE_APPLY_ACTION_ROOTS = (
    "make final-apply-resources",
    "run make final-apply-resources",
)
PROVIDER_SELECTION_ACTION_ROOTS = (
    "set THREE_D_PROVIDER=meshy",
    "set NPC_PROVIDER=openai",
)
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
FINAL_RESOURCES_PREFLIGHT_COMMAND = "make final-resources-preflight"
MOBILE_DEPLOY_PREFLIGHT_COMMAND = "make mobile-deploy-preflight"
UNBLOCK_ACTION_REPLACEMENTS = {
    "unblock final_resource_fill_guide after MESHY_API_KEY": (
        "provide MESHY_API_KEY in final-resources.env; "
        f"rerun {FINAL_RESOURCES_PREFLIGHT_COMMAND}"
    ),
    "unblock provider_handoff before configured evidence bundle": (
        "make provider-handoff"
    ),
}
BACKEND_DEVICE_DEMO_ACTION = (
    "start backend-device-demo before device checks: make backend-device-demo"
)
BACKEND_DEVICE_DEMO_VALIDATED_ACTION = (
    f"{BACKEND_DEVICE_DEMO_ACTION}; rerun {MOBILE_DEPLOY_PREFLIGHT_COMMAND}"
)
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
    "provide DEVELOPMENT_TEAM in Deployment.local.xcconfig",
    "provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig",
    "provide PMF_BACKEND_BASE_URL in Deployment.local.xcconfig",
    "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL",
    "set PMF_FINAL_LAUNCH_MODE to local or configured",
)


def normalize_operator_action(action: str) -> str:
    normalized = action.strip()
    command_part, detail_suffix = _split_detail_suffix(normalized)
    legacy_action = _normalize_legacy_action(command_part)
    if legacy_action is not None:
        return f"{legacy_action}{detail_suffix}"
    unblock_action = _normalize_unblock_action(command_part)
    if unblock_action is not None:
        return f"{unblock_action}{detail_suffix}"
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
        return f"{_replace_action_command(command_part, command)}{detail_suffix}"
    return f"{command_part}{detail_suffix}"


def _normalize_unblock_action(action: str) -> str | None:
    if action in UNBLOCK_ACTION_REPLACEMENTS:
        return UNBLOCK_ACTION_REPLACEMENTS[action]
    for vague, replacement in UNBLOCK_ACTION_REPLACEMENTS.items():
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
