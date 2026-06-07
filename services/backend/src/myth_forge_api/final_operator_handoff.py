from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from myth_forge_api.final_acceptance_readiness import LOCAL_FINAL_ACCEPTANCE_COMMAND
from myth_forge_api.ios_deploy_runbook import IOS_DEPLOY_RUNBOOK_COMMAND
from myth_forge_api.npc_agent_evaluation_readiness import LOCAL_NPC_EVALUATION_COMMAND
from myth_forge_api.three_d_evaluation_readiness import LOCAL_THREE_D_EVALUATION_COMMAND

LaunchMode = Literal["local", "configured"]

CONFIGURED_FINAL_ACCEPTANCE_COMMAND = (
    "cd services/backend && uv run python -m myth_forge_api.cli "
    "final-acceptance --profile quick --provider-mode configured "
    "--require-real-core --allow-live-provider-calls --repo-root ../.. "
    "--output .local/final-acceptance-configured.json"
)

STEP_ORDER = [
    "final_resources_preflight",
    "apply_final_resources",
    "backend_device_server",
    "local_final_acceptance",
    "three_d_evaluation",
    "npc_agent_evaluation",
    "ios_deploy_runbook",
    "mobile_deploy_preflight",
    "xcode_build_gate",
    "configured_final_acceptance",
]


def build_final_operator_handoff_report(
    *,
    mode: LaunchMode,
    final_resources_preflight: dict[str, Any],
    final_acceptance_readiness: dict[str, Any],
    three_d_evaluation_readiness: dict[str, Any],
    npc_agent_evaluation_readiness: dict[str, Any],
    ios_deploy_runbook: dict[str, Any],
    launch_phases: list[dict[str, Any]],
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    if mode not in ("local", "configured"):
        raise ValueError(f"Unsupported final operator handoff mode: {mode}")
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    phases = {str(phase.get("id", "")): phase for phase in launch_phases}
    blockers = _acceptance_blockers(final_acceptance_readiness)
    steps = [
        _resources_preflight_step(final_resources_preflight),
        _phase_step(
            phase_id="apply_final_resources",
            phases=phases,
            fallback_label="Apply final resources",
            fallback_command="make final-apply-resources",
        ),
        _phase_step(
            phase_id="backend_device_server",
            phases=phases,
            fallback_label="Start backend on LAN",
            fallback_command="make backend-device-demo",
        ),
        _local_acceptance_step(final_acceptance_readiness, phases),
        _three_d_evaluation_step(three_d_evaluation_readiness),
        _npc_evaluation_step(npc_agent_evaluation_readiness),
        _ios_deploy_runbook_step(ios_deploy_runbook),
        _acceptance_or_phase_step(
            step_id="mobile_deploy_preflight",
            blocker_id="mobile_deploy_preflight",
            phases=phases,
            blockers=blockers,
            fallback_label="Run iOS deploy preflight",
            fallback_command="make mobile-deploy-preflight",
        ),
        _acceptance_or_phase_step(
            step_id="xcode_build_gate",
            blocker_id="mobile_xcode_build",
            phases=phases,
            blockers=blockers,
            fallback_label="Run Xcode build gate",
            fallback_command="make mobile-xcode-build",
        ),
        _configured_acceptance_step(mode=mode, phases=phases),
    ]
    summary = _summary(steps)
    report = {
        "kind": "final_operator_handoff_report",
        "mode": mode,
        "status": _overall_status(summary),
        "summary": summary,
        "steps": steps,
        "next_actions": _next_actions(
            mode=mode,
            final_resources_preflight=final_resources_preflight,
            final_acceptance_readiness=final_acceptance_readiness,
            three_d_evaluation_readiness=three_d_evaluation_readiness,
            npc_agent_evaluation_readiness=npc_agent_evaluation_readiness,
            ios_deploy_runbook=ios_deploy_runbook,
            steps=steps,
        ),
        "safety": {
            "commands_run": False,
            "provider_calls": False,
            "global_mutation": False,
            "provider_secrets_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
            "local_paths_in_report": False,
            "command_execution_from_app": False,
        },
    }
    return _sanitize_report(report, selected_repo_root)


def _resources_preflight_step(report: dict[str, Any]) -> dict[str, Any]:
    return _step(
        step_id="final_resources_preflight",
        label="Final resources preflight",
        status=str(report.get("status", "missing")),
        command="make final-resources-preflight",
        required_for="one-file backend and iOS final demo handoff",
        source="final_resources_preflight",
        notes=[
            "Validates ignored services/backend/.local/final-resources.env without applying it."
        ],
    )


def _phase_step(
    *,
    phase_id: str,
    phases: dict[str, dict[str, Any]],
    fallback_label: str,
    fallback_command: str,
) -> dict[str, Any]:
    phase = phases.get(phase_id, {})
    return _step(
        step_id=phase_id,
        label=str(phase.get("label", fallback_label)),
        status=str(phase.get("status", "missing")),
        command=str(phase.get("command", fallback_command)),
        required_for=str(phase.get("required_for", "final demo")),
        source="final_demo_launch_phase",
        notes=_string_list(phase.get("notes")),
    )


def _local_acceptance_step(
    readiness: dict[str, Any],
    phases: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    phase = phases.get("local_final_acceptance", {})
    status = str(readiness.get("status", phase.get("status", "missing")))
    return _step(
        step_id="local_final_acceptance",
        label=str(phase.get("label", "Run local final acceptance")),
        status=status,
        command=LOCAL_FINAL_ACCEPTANCE_COMMAND,
        required_for=str(phase.get("required_for", "no-key deterministic smoke acceptance")),
        source="final_acceptance_readiness",
        notes=_string_list(phase.get("notes")) + _acceptance_notes(readiness),
    )


def _acceptance_or_phase_step(
    *,
    step_id: str,
    blocker_id: str,
    phases: dict[str, dict[str, Any]],
    blockers: dict[str, dict[str, Any]],
    fallback_label: str,
    fallback_command: str,
) -> dict[str, Any]:
    blocker = blockers.get(blocker_id)
    if blocker is not None:
        return _step(
            step_id=step_id,
            label=str(blocker.get("label", fallback_label)),
            status=str(blocker.get("status", "blocked")),
            command=str(blocker.get("command", fallback_command)),
            required_for="final acceptance",
            source="final_acceptance_readiness",
            notes=[
                str(blocker.get("classification", "blocked")),
                str(blocker.get("detail", "")),
            ],
        )
    return _phase_step(
        phase_id=step_id,
        phases=phases,
        fallback_label=fallback_label,
        fallback_command=fallback_command,
    )


def _npc_evaluation_step(readiness: dict[str, Any]) -> dict[str, Any]:
    status = str(readiness.get("status", "missing"))
    notes = _npc_evaluation_notes(readiness)
    if status == "ready":
        mapped_status = "ready"
    elif status == "missing":
        mapped_status = "missing"
    elif status in {"blocked", "failed"}:
        mapped_status = "blocked"
    else:
        mapped_status = "blocked"
        notes.append("unknown_npc_evaluation_status")
    return _step(
        step_id="npc_agent_evaluation",
        label="Run NPC Agent evaluation",
        status=mapped_status,
        command=LOCAL_NPC_EVALUATION_COMMAND,
        required_for="AI Agent NPC final demo readiness",
        source="npc_agent_evaluation_readiness",
        notes=notes,
    )


def _three_d_evaluation_step(readiness: dict[str, Any]) -> dict[str, Any]:
    status = str(readiness.get("status", "missing"))
    notes = _three_d_evaluation_notes(readiness)
    if status == "ready":
        mapped_status = "ready"
    elif status == "missing":
        mapped_status = "missing"
    elif status in {"blocked", "failed"}:
        mapped_status = "blocked"
    else:
        mapped_status = "blocked"
        notes.append("unknown_three_d_evaluation_status")
    return _step(
        step_id="three_d_evaluation",
        label="Run 3D evaluation",
        status=mapped_status,
        command=LOCAL_THREE_D_EVALUATION_COMMAND,
        required_for="3D provider final demo readiness",
        source="three_d_evaluation_readiness",
        notes=notes,
    )


def _ios_deploy_runbook_step(runbook: dict[str, Any]) -> dict[str, Any]:
    status = str(runbook.get("status", "missing"))
    if status not in {"ready", "partial", "blocked", "missing"}:
        status = "blocked"
    return _step(
        step_id="ios_deploy_runbook",
        label="Review iOS deploy runbook",
        status=status,
        command=IOS_DEPLOY_RUNBOOK_COMMAND,
        required_for="physical iPhone deploy command handoff",
        source="ios_deploy_runbook",
        notes=_ios_deploy_runbook_notes(runbook),
    )


def _configured_acceptance_step(
    *,
    mode: LaunchMode,
    phases: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    phase = phases.get("configured_final_acceptance", {})
    phase_status = str(phase.get("status", "optional"))
    status = phase_status
    requires_consent = False
    notes = _string_list(phase.get("notes"))
    if phase_status == "ready" and mode == "configured":
        status = "live"
        requires_consent = True
        notes.append("May call live providers and spend provider credits.")
    return _step(
        step_id="configured_final_acceptance",
        label=str(phase.get("label", "Run configured final acceptance")),
        status=status,
        command=str(phase.get("command", CONFIGURED_FINAL_ACCEPTANCE_COMMAND)),
        required_for=str(phase.get("required_for", "real 3D and AI NPC provider acceptance")),
        source="final_demo_launch_phase",
        notes=notes,
        requires_consent=requires_consent,
    )


def _step(
    *,
    step_id: str,
    label: str,
    status: str,
    command: str,
    required_for: str,
    source: str,
    notes: list[str],
    requires_consent: bool = False,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "label": label,
        "status": status,
        "command": command,
        "required_for": required_for,
        "source": source,
        "notes": [note for note in notes if note],
        "requires_consent": requires_consent,
    }


def _acceptance_blockers(readiness: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_blockers = readiness.get("blockers", [])
    if not isinstance(raw_blockers, list):
        return {}
    return {
        str(blocker.get("id", "unknown_check")): blocker
        for blocker in raw_blockers
        if isinstance(blocker, dict)
    }


def _acceptance_notes(readiness: dict[str, Any]) -> list[str]:
    summary = readiness.get("summary", {})
    if not isinstance(summary, dict):
        return []
    blocked = summary.get("blocked", 0)
    failed = summary.get("failed", 0)
    if blocked or failed:
        return [f"Final acceptance has {blocked} blocked and {failed} failed checks."]
    return []


def _npc_evaluation_notes(readiness: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    summary = readiness.get("summary", {})
    if isinstance(summary, dict):
        succeeded = summary.get("succeeded", 0)
        failed = summary.get("failed", 0)
        notes.append(f"NPC evaluation has {succeeded} succeeded and {failed} failed cases.")
    blockers = readiness.get("blockers", [])
    if isinstance(blockers, list) and blockers:
        blocker = blockers[0]
        if isinstance(blocker, dict):
            notes.append(str(blocker.get("classification", "blocked")))
            notes.append(str(blocker.get("detail", "")))
    return notes


def _three_d_evaluation_notes(readiness: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    summary = readiness.get("summary", {})
    if isinstance(summary, dict):
        succeeded = summary.get("succeeded", 0)
        failed = summary.get("failed", 0)
        notes.append(f"3D evaluation has {succeeded} succeeded and {failed} failed cases.")
    coverage = readiness.get("coverage", {})
    if isinstance(coverage, dict):
        scene_loadable = coverage.get("scene_loadable_cases", 0)
        notes.append(f"3D evaluation has {scene_loadable} scene-loadable cases.")
    blockers = readiness.get("blockers", [])
    if isinstance(blockers, list) and blockers:
        blocker = blockers[0]
        if isinstance(blocker, dict):
            notes.append(str(blocker.get("classification", "blocked")))
            notes.append(str(blocker.get("detail", "")))
    return notes


def _ios_deploy_runbook_notes(runbook: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    input_slots = runbook.get("input_slots", [])
    command_sequence = runbook.get("command_sequence", [])
    if isinstance(input_slots, list):
        missing = sum(
            1
            for slot in input_slots
            if isinstance(slot, dict) and slot.get("status") == "missing"
        )
        blocked = sum(
            1
            for slot in input_slots
            if isinstance(slot, dict) and slot.get("status") == "blocked"
        )
        notes.append(
            f"iOS deploy runbook has {missing} missing and {blocked} blocked input slots."
        )
    if isinstance(command_sequence, list):
        notes.append(f"iOS deploy runbook has {len(command_sequence)} command steps.")
    return notes


def _next_actions(
    *,
    mode: LaunchMode,
    final_resources_preflight: dict[str, Any],
    final_acceptance_readiness: dict[str, Any],
    three_d_evaluation_readiness: dict[str, Any],
    npc_agent_evaluation_readiness: dict[str, Any],
    ios_deploy_runbook: dict[str, Any],
    steps: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    actions.extend(_string_list(final_resources_preflight.get("operator_actions")))
    readiness_actions = [
        action
        for action in _string_list(final_acceptance_readiness.get("operator_actions"))
        if action != "final acceptance is ready"
    ]
    actions.extend(readiness_actions)
    three_d_step = next((step for step in steps if step["id"] == "three_d_evaluation"), None)
    if three_d_step is not None and three_d_step["status"] in {"missing", "blocked"}:
        three_d_actions = [
            action
            for action in _string_list(three_d_evaluation_readiness.get("operator_actions"))
            if action != "3D evaluation is ready"
        ]
        actions.extend(three_d_actions)
    npc_step = next((step for step in steps if step["id"] == "npc_agent_evaluation"), None)
    if npc_step is not None and npc_step["status"] in {"missing", "blocked"}:
        npc_actions = [
            action
            for action in _string_list(npc_agent_evaluation_readiness.get("operator_actions"))
            if action != "NPC Agent evaluation is ready"
        ]
        actions.extend(npc_actions)
    runbook_step = next((step for step in steps if step["id"] == "ios_deploy_runbook"), None)
    if runbook_step is not None and runbook_step["status"] in {"missing", "blocked"}:
        actions.extend(_string_list(ios_deploy_runbook.get("operator_actions")))
    if mode == "configured" and any(
        step["id"] == "configured_final_acceptance" and step["status"] == "live"
        for step in steps
    ):
        actions.append(
            "run configured final acceptance only after live provider cost review "
            "and --allow-live-provider-calls consent"
        )
    for step in steps:
        if step["status"] in {"missing", "blocked"}:
            if step["id"] in {"final_resources_preflight", "local_final_acceptance"}:
                continue
            if step["source"] == "final_acceptance_readiness":
                continue
            if step["source"] == "three_d_evaluation_readiness":
                continue
            if step["source"] == "npc_agent_evaluation_readiness":
                continue
            if step["source"] == "ios_deploy_runbook":
                continue
            actions.append(f"unblock {step['id']}: {step['command']}")
        if step["status"] == "manual" and step["id"] == "xcode_build_gate":
            actions.append(f"run Xcode build gate manually on the Mac: {step['command']}")
    return _dedupe(actions)


def _summary(steps: list[dict[str, Any]]) -> dict[str, int]:
    statuses = ["ready", "missing", "blocked", "manual", "optional", "partial", "live"]
    return {
        status: sum(1 for step in steps if step["status"] == status)
        for status in statuses
    }


def _overall_status(summary: dict[str, int]) -> str:
    if summary["missing"] or summary["blocked"]:
        return "blocked"
    if summary["manual"] or summary["optional"] or summary["partial"] or summary["live"]:
        return "partial"
    return "ready"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    return json.loads(json.dumps(_sanitize_value(report, repo_root)))


def _sanitize_value(value: Any, repo_root: Path) -> Any:
    if isinstance(value, str):
        return _safe_text(value, repo_root)
    if isinstance(value, list):
        return [_sanitize_value(item, repo_root) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item, repo_root) for key, item in value.items()}
    return value


def _safe_text(message: str, repo_root: Path) -> str:
    sanitized = message
    patterns = [
        r"sk-[A-Za-z0-9._-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"file://[^\s,;\"']+",
        r"private_message:[^\n\r]+",
        r"raw_context:[^\n\r]+",
        r"message_body:[^\n\r]+",
    ]
    for pattern in patterns:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    root_text = str(repo_root)
    if root_text:
        sanitized = sanitized.replace(root_text, "[repo-root]")
    home_text = str(Path.home())
    if home_text:
        sanitized = sanitized.replace(home_text, "[home]")
    return sanitized


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
