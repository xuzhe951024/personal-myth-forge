from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.configured_acceptance_command import CONFIGURED_FINAL_ACCEPTANCE_COMMAND
from myth_forge_api.config import Settings, load_settings
from myth_forge_api.final_configured_preflight import (
    build_final_configured_preflight_report,
)
from myth_forge_api.final_resource_apply_preview import (
    build_final_resource_apply_preview_report,
)
from myth_forge_api.final_resource_fill_guide import (
    build_final_resource_fill_guide_report,
)
from myth_forge_api.live_provider_evidence import build_live_provider_evidence_report


@dataclass(frozen=True)
class FinalConfiguredEvidencePlanResult:
    exit_code: int
    report: dict[str, Any]


@dataclass(frozen=True)
class StepDefinition:
    step_id: str
    label: str
    command: str
    requires_live_provider_consent: bool = False
    may_call_live_provider: bool = False
    cost_risk: bool = False
    repo_local_write: bool = False
    would_write_backend_env: bool = False
    would_write_ios_deploy_config: bool = False
    evidence_slot_id: str | None = None


STEPS = [
    StepDefinition(
        step_id="final_resource_fill_guide",
        label="Final resource fill guide",
        command="make final-resource-fill-guide",
    ),
    StepDefinition(
        step_id="final_resource_apply_preview",
        label="Final resource apply preview",
        command="make final-resource-apply-preview",
    ),
    StepDefinition(
        step_id="final_apply_resources",
        label="Apply final resources",
        command="make final-apply-resources",
        repo_local_write=True,
        would_write_backend_env=True,
        would_write_ios_deploy_config=True,
    ),
    StepDefinition(
        step_id="final_configured_preflight",
        label="Final configured preflight",
        command="make final-configured-preflight",
    ),
    StepDefinition(
        step_id="provider_handoff",
        label="Provider handoff",
        command=(
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "provider-handoff --require-core-real --output .local/provider-handoff.json"
        ),
        evidence_slot_id="provider_handoff",
    ),
    StepDefinition(
        step_id="three_d_evaluation_configured",
        label="Configured 3D evaluation",
        command="make backend-evaluate-3d-configured",
        requires_live_provider_consent=True,
        may_call_live_provider=True,
        cost_risk=True,
        evidence_slot_id="three_d_evaluation_configured",
    ),
    StepDefinition(
        step_id="npc_evaluation_configured",
        label="Configured NPC Agent evaluation",
        command="make backend-evaluate-npc-configured",
        requires_live_provider_consent=True,
        may_call_live_provider=True,
        cost_risk=True,
        evidence_slot_id="npc_evaluation_configured",
    ),
    StepDefinition(
        step_id="final_acceptance_configured",
        label="Configured final acceptance",
        command=CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
        requires_live_provider_consent=True,
        may_call_live_provider=True,
        cost_risk=True,
        evidence_slot_id="final_acceptance_configured",
    ),
    StepDefinition(
        step_id="final_demo_launch_configured",
        label="Configured final demo launch",
        command=(
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "final-demo-launch --mode configured --repo-root ../.. "
            "--output .local/final-demo-launch-configured.json"
        ),
        evidence_slot_id="final_demo_launch_configured",
    ),
    StepDefinition(
        step_id="live_provider_evidence",
        label="Live provider evidence",
        command="make live-provider-evidence",
    ),
]


def build_final_configured_evidence_plan_report(
    *,
    repo_root: Path | str | None = None,
    settings: Settings | None = None,
    allow_live_provider_calls: bool = False,
) -> FinalConfiguredEvidencePlanResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_settings = settings or load_settings()
    fill_guide = build_final_resource_fill_guide_report(
        repo_root=selected_repo_root,
    ).report
    apply_preview = build_final_resource_apply_preview_report(
        repo_root=selected_repo_root,
    ).report
    configured_preflight = build_final_configured_preflight_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    ).report
    live_evidence = build_live_provider_evidence_report(
        repo_root=selected_repo_root,
    ).report
    evidence_by_id = {
        str(row.get("id")): row
        for row in live_evidence.get("evidence", [])
        if isinstance(row, dict)
    }
    steps = [
        _step_row(
            definition=definition,
            fill_guide=fill_guide,
            apply_preview=apply_preview,
            configured_preflight=configured_preflight,
            live_evidence=live_evidence,
            evidence_by_id=evidence_by_id,
            allow_live_provider_calls=allow_live_provider_calls,
        )
        for definition in STEPS
    ]
    status = _overall_status(steps)
    report = {
        "kind": "final_configured_evidence_plan_report",
        "status": status,
        "summary": _summary(steps),
        "steps": steps,
        "steps_by_id": {step["id"]: step for step in steps},
        "source_reports": {
            "final_resource_fill_guide": _source_summary(fill_guide),
            "final_resource_apply_preview": _source_summary(apply_preview),
            "final_configured_preflight": _source_summary(configured_preflight),
            "live_provider_evidence": _source_summary(live_evidence),
        },
        "operator_actions": _operator_actions(steps),
        "commands": [step.command for step in STEPS],
        "live_call_policy": {
            "live_calls_by_default": False,
            "allow_live_provider_calls": allow_live_provider_calls,
            "consent_flag": "--allow-live-provider-calls",
            "consent_required_for": [
                step.step_id for step in STEPS if step.requires_live_provider_consent
            ],
        },
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return FinalConfiguredEvidencePlanResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _step_row(
    *,
    definition: StepDefinition,
    fill_guide: dict[str, Any],
    apply_preview: dict[str, Any],
    configured_preflight: dict[str, Any],
    live_evidence: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]],
    allow_live_provider_calls: bool,
) -> dict[str, Any]:
    status, blocked_by = _step_status(
        definition=definition,
        fill_guide=fill_guide,
        apply_preview=apply_preview,
        configured_preflight=configured_preflight,
        live_evidence=live_evidence,
        evidence_by_id=evidence_by_id,
        allow_live_provider_calls=allow_live_provider_calls,
    )
    if status not in {"blocked", "consent_required"}:
        blocked_by = []
    evidence = (
        evidence_by_id.get(definition.evidence_slot_id)
        if definition.evidence_slot_id is not None
        else None
    )
    row = {
        "id": definition.step_id,
        "label": definition.label,
        "status": status,
        "command": definition.command,
        "requires_live_provider_consent": definition.requires_live_provider_consent,
        "may_call_live_provider": definition.may_call_live_provider,
        "cost_risk": definition.cost_risk,
        "repo_local_write": definition.repo_local_write,
        "would_write_backend_env": definition.would_write_backend_env,
        "would_write_ios_deploy_config": definition.would_write_ios_deploy_config,
        "blocked_by": blocked_by,
    }
    if evidence is not None:
        row["evidence_status"] = str(evidence.get("status", "missing"))
        row["evidence_path"] = str(evidence.get("path", ""))
        row["evidence_detail"] = str(evidence.get("detail", ""))
    return row


def _step_status(
    *,
    definition: StepDefinition,
    fill_guide: dict[str, Any],
    apply_preview: dict[str, Any],
    configured_preflight: dict[str, Any],
    live_evidence: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]],
    allow_live_provider_calls: bool,
) -> tuple[str, list[str]]:
    fill_ready = fill_guide.get("status") == "ready"
    apply_ready = apply_preview.get("status") == "ready"
    configured_ready = configured_preflight.get("status") == "ready"
    live_evidence_ready = live_evidence.get("status") == "ready"
    evidence_status = "missing"
    if definition.evidence_slot_id is not None:
        evidence_status = str(
            evidence_by_id.get(definition.evidence_slot_id, {}).get(
                "status",
                "missing",
            )
        )

    if definition.step_id == "final_resource_fill_guide":
        return _source_step_status(fill_guide), _blocked_by_source(fill_guide)
    if definition.step_id == "final_resource_apply_preview":
        if fill_ready:
            return _source_step_status(apply_preview), _blocked_by_source(apply_preview)
        return "blocked", ["final_resource_fill_guide"]
    if definition.step_id == "final_apply_resources":
        if apply_ready:
            if live_evidence_ready:
                return "ready", []
            return "ready_to_run", []
        return "blocked", ["final_resource_apply_preview"]
    if definition.step_id == "final_configured_preflight":
        if fill_ready and apply_ready:
            return _source_step_status(configured_preflight), _blocked_by_source(
                configured_preflight
            )
        return "blocked", ["final_apply_resources"]
    if definition.step_id == "live_provider_evidence":
        if live_evidence_ready:
            return "ready", []
        if configured_ready:
            return "ready_to_run", []
        return "blocked", ["final_configured_preflight"]

    if not configured_ready:
        return "blocked", ["final_configured_preflight"]
    if evidence_status == "ready":
        return "ready", []
    if definition.requires_live_provider_consent and not allow_live_provider_calls:
        return "consent_required", ["live_provider_cost_consent"]
    if definition.step_id == "final_demo_launch_configured" and not (
        live_evidence_ready or allow_live_provider_calls
    ):
        return "consent_required", ["configured_live_evidence"]
    return "ready_to_run", []


def _source_step_status(report: dict[str, Any]) -> str:
    status = str(
        report.get("status")
        or report.get("overall_status")
        or "blocked"
    )
    if status in {"ready", "passed"}:
        return "ready"
    return "blocked"


def _blocked_by_source(report: dict[str, Any]) -> list[str]:
    first_blocker = report.get("first_blocker")
    if isinstance(first_blocker, dict) and first_blocker.get("id"):
        return [str(first_blocker["id"])]
    actions = report.get("operator_actions")
    if isinstance(actions, list) and actions:
        return [str(actions[0])]
    return []


def _overall_status(steps: list[dict[str, Any]]) -> str:
    statuses = [str(step["status"]) for step in steps]
    if "blocked" in statuses:
        return "blocked"
    if "consent_required" in statuses:
        return "consent_required"
    if "ready_to_run" in statuses:
        return "ready_to_run"
    return "ready"


def _summary(steps: list[dict[str, Any]]) -> dict[str, int]:
    statuses = [str(step["status"]) for step in steps]
    return {
        "steps": len(steps),
        "ready": statuses.count("ready"),
        "ready_to_run": statuses.count("ready_to_run"),
        "blocked": statuses.count("blocked"),
        "consent_required": statuses.count("consent_required"),
        "planned_consent_steps": sum(
            1
            for step in steps
            if step["requires_live_provider_consent"] and step["status"] != "ready"
        ),
        "live_provider_steps": sum(1 for step in steps if step["may_call_live_provider"]),
        "cost_steps": sum(1 for step in steps if step["cost_risk"]),
        "repo_local_write_steps": sum(1 for step in steps if step["repo_local_write"]),
        "commands_run": 0,
    }


def _source_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": report.get("kind", "unknown"),
        "status": report.get("status", report.get("overall_status", "unknown")),
        "summary": report.get("summary", {}),
    }


def _operator_actions(steps: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for step in steps:
        status = str(step["status"])
        if status == "blocked":
            blocked_by = step.get("blocked_by", [])
            suffix = f" after {', '.join(blocked_by)}" if blocked_by else ""
            actions.append(f"unblock {step['id']}{suffix}")
        elif status == "consent_required":
            actions.append(
                f"review live provider cost consent before {step['id']}"
            )
    if not actions:
        actions.append("run configured evidence commands in order")
    return _dedupe(actions)[:12]


def _safety() -> dict[str, bool]:
    return {
        "commands_run": False,
        "provider_calls": False,
        "live_provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "raw_private_context_in_report": False,
        "raw_media_in_report": False,
        "payment_links_in_report": False,
        "local_paths_in_report": False,
    }


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


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
        r"meshy-secret-[A-Za-z0-9._-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"file://[^\s,;\"']+",
        r"/private/[^\s,;\"']+",
        r"/tmp/[^\s,;\"']+",
        r"/Users/[^\s,;\"']+",
        r"https?://10\.[^\s,;\"'`]+",
        r"https?://192\.168\.[^\s,;\"'`]+",
        r"https?://172\.(?:1[6-9]|2[0-9]|3[01])\.[^\s,;\"'`]+",
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


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
