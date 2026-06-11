from __future__ import annotations

LEGACY_FINAL_RESOURCE_COPY_MARKERS = (
    "services/backend/final-resources.env.example",
    "services/backend/.local/final-resources.env",
)
NORMALIZED_FINAL_RESOURCE_INIT_ACTION = "run make final-resource-init"
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


def normalize_operator_action(action: str) -> str:
    normalized = action.strip()
    if all(marker in normalized for marker in LEGACY_FINAL_RESOURCE_COPY_MARKERS):
        return NORMALIZED_FINAL_RESOURCE_INIT_ACTION
    if normalized.endswith(f": {NORMALIZED_FINAL_RESOURCE_INIT_ACTION}"):
        return NORMALIZED_FINAL_RESOURCE_INIT_ACTION
    command = _normalized_command(normalized)
    if command is not None:
        return _replace_action_command(normalized, command)
    return normalized


def add_final_resource_validation_command(action: str) -> str:
    normalized = action.strip()
    root = normalized.split("; rerun ", 1)[0].strip()
    if root.endswith(FINAL_RESOURCE_VALIDATION_ACTION_ROOTS):
        return f"{root}; rerun {FINAL_RESOURCES_PREFLIGHT_COMMAND}"
    if "; rerun " in normalized:
        return normalized
    return normalized


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
