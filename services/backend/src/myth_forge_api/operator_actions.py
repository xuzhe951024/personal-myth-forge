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
