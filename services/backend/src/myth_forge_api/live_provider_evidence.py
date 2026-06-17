from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myth_forge_api.configured_acceptance_command import CONFIGURED_FINAL_ACCEPTANCE_COMMAND
from myth_forge_api.final_handoff_commands import (
    FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
    PROVIDER_HANDOFF_COMMAND,
)
from myth_forge_api.operator_actions import normalize_operator_action

LIVE_PROVIDER_CONSENT_ENV_PREFIX = "PMF_ALLOW_LIVE_PROVIDER_CALLS=1 "


@dataclass(frozen=True)
class LiveProviderEvidenceResult:
    exit_code: int
    report: dict[str, Any]


@dataclass(frozen=True)
class EvidenceSlot:
    slot_id: str
    label: str
    path: Path
    expected_kind: str
    command: str
    proof: str
    requires_live_provider_consent: bool
    rerun_action: str


EVIDENCE_SLOTS = [
    EvidenceSlot(
        slot_id="provider_handoff",
        label="Provider handoff",
        path=Path("services/backend/.local/provider-handoff.json"),
        expected_kind="provider_handoff_report",
        command=PROVIDER_HANDOFF_COMMAND,
        proof="Meshy and OpenAI core provider config is real-provider-ready.",
        requires_live_provider_consent=False,
        rerun_action="rerun provider handoff readiness",
    ),
    EvidenceSlot(
        slot_id="three_d_evaluation_configured",
        label="Configured 3D evaluation",
        path=Path("services/backend/.local/3d-evaluation-configured.json"),
        expected_kind="three_d_evaluation_report",
        command="make backend-evaluate-3d-configured",
        proof="Meshy generated the canonical 20-case 3D suite for review.",
        requires_live_provider_consent=True,
        rerun_action="rerun configured 3D evaluation",
    ),
    EvidenceSlot(
        slot_id="npc_evaluation_configured",
        label="Configured NPC Agent evaluation",
        path=Path("services/backend/.local/npc-evaluation-configured.json"),
        expected_kind="npc_agent_evaluation_report",
        command="make backend-evaluate-npc-configured",
        proof="OpenAI NPC Agent ticks completed the canonical NPC suite.",
        requires_live_provider_consent=True,
        rerun_action="rerun configured NPC Agent evaluation",
    ),
    EvidenceSlot(
        slot_id="final_acceptance_configured",
        label="Configured final acceptance",
        path=Path("services/backend/.local/final-acceptance-configured.json"),
        expected_kind="final_acceptance_report",
        command=CONFIGURED_FINAL_ACCEPTANCE_COMMAND,
        proof="Configured quick acceptance ran with real providers and consent.",
        requires_live_provider_consent=True,
        rerun_action="rerun make final-acceptance-configured",
    ),
    EvidenceSlot(
        slot_id="final_demo_launch_configured",
        label="Configured final demo launch",
        path=Path("services/backend/.local/final-demo-launch-configured.json"),
        expected_kind="final_demo_launch_report",
        command=FINAL_DEMO_LAUNCH_CONFIGURED_COMMAND,
        proof="Configured final launch packet was regenerated after live evidence.",
        requires_live_provider_consent=False,
        rerun_action="rerun configured final demo launch",
    ),
]


def build_live_provider_evidence_report(
    *,
    repo_root: Path | str | None = None,
) -> LiveProviderEvidenceResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    evidence = [
        _evidence_row(slot=slot, repo_root=selected_repo_root)
        for slot in EVIDENCE_SLOTS
    ]
    summary = _summary(evidence)
    status = _overall_status(summary)
    first_blocker = _first_blocker(evidence)
    operator_actions = _operator_actions(
        status=status,
        evidence=evidence,
        first_blocker=first_blocker,
    )
    report = {
        "kind": "live_provider_evidence_report",
        "status": status,
        "summary": summary,
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "evidence": evidence,
        "operator_actions": operator_actions,
        "commands": ["make live-provider-evidence", *[slot.command for slot in EVIDENCE_SLOTS]],
        "safety": _safety(),
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return LiveProviderEvidenceResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _evidence_row(*, slot: EvidenceSlot, repo_root: Path) -> dict[str, Any]:
    path = repo_root / slot.path
    base = {
        "id": slot.slot_id,
        "label": slot.label,
        "path": slot.path.as_posix(),
        "exists": path.exists(),
        "expected_kind": slot.expected_kind,
        "command": slot.command,
        "proof": slot.proof,
        "requires_live_provider_consent": slot.requires_live_provider_consent,
    }
    base.update(_slot_live_confirmation_metadata(slot))
    if not path.exists():
        return base | {
            "status": "missing",
            "classification": "missing_report",
            "detail": f"Missing {slot.path.as_posix()}.",
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return base | {
            "status": "blocked",
            "classification": "unreadable_report",
            "detail": "Saved evidence report is not valid JSON.",
        }

    if not isinstance(payload, dict):
        return base | {
            "status": "blocked",
            "classification": "invalid_report_shape",
            "detail": "Saved evidence report must be a JSON object.",
        }

    if payload.get("kind") != slot.expected_kind:
        return base | {
            "status": "blocked",
            "classification": "wrong_report_kind",
            "detail": f"Expected {slot.expected_kind}.",
        }

    status = _status_from_payload(slot, payload)
    row = base | {
        "status": status,
        "classification": _classification_for_status(status),
        "detail": _detail_from_payload(slot, payload, status=status),
    }
    source_blocker = _provider_handoff_source_blocker(slot, payload, status=status)
    if source_blocker is not None:
        command = str(source_blocker.get("source_blocker_command", "")).strip()
        detail = str(source_blocker.get("source_blocker_detail", "")).strip()
        row = row | source_blocker
        if command:
            row["command"] = command
        if detail:
            row["detail"] = detail
    return row


def _status_from_payload(slot: EvidenceSlot, payload: dict[str, Any]) -> str:
    if slot.slot_id == "provider_handoff":
        return "ready" if payload.get("core_real_ready") is True else "blocked"
    if slot.slot_id == "three_d_evaluation_configured":
        return _evaluation_status(payload)
    if slot.slot_id == "npc_evaluation_configured":
        return _evaluation_status(payload)
    if slot.slot_id == "final_acceptance_configured":
        status = str(payload.get("overall_status", "blocked"))
        if status in {"passed", "ready"}:
            return "ready"
        if status in {"partial", "blocked"}:
            return status
        return "blocked"
    if slot.slot_id == "final_demo_launch_configured":
        status = str(payload.get("overall_status", "blocked"))
        if status == "ready":
            return "ready"
        if status == "partial":
            return "partial"
        return "blocked"
    return "blocked"


def _evaluation_status(payload: dict[str, Any]) -> str:
    succeeded = _non_negative_int(payload.get("succeeded"))
    failed = _non_negative_int(payload.get("failed"))
    if succeeded > 0 and failed == 0:
        return "ready"
    return "blocked"


def _classification_for_status(status: str) -> str:
    if status == "ready":
        return "ready"
    if status == "missing":
        return "missing_report"
    if status == "partial":
        return "report_partial"
    return "report_not_ready"


def _detail_from_payload(
    slot: EvidenceSlot,
    payload: dict[str, Any],
    *,
    status: str,
) -> str:
    if status == "ready":
        return slot.proof
    if status == "partial":
        return "Saved report is useful for review but not final-ready."
    errors = payload.get("errors")
    if isinstance(errors, list) and errors:
        return str(errors[0])
    if slot.slot_id == "provider_handoff":
        missing = payload.get("missing_env")
        if isinstance(missing, list) and missing:
            return "Missing provider env: " + ", ".join(str(item) for item in missing)
        if payload.get("core_real_ready") is False:
            return "Core real providers are not ready for live evidence."
    return "Saved report is not ready."


def _provider_handoff_source_blocker(
    slot: EvidenceSlot,
    payload: dict[str, Any],
    *,
    status: str,
) -> dict[str, str] | None:
    if slot.slot_id != "provider_handoff" or status == "ready":
        return None
    for key in ("next_action", "first_blocker"):
        candidate = payload.get(key)
        if not isinstance(candidate, dict):
            continue
        command = str(candidate.get("command", "")).strip()
        if not command:
            continue
        source = {
            "source_blocker_command": command,
        }
        for source_key, target_key in (
            ("id", "source_blocker_id"),
            ("label", "source_blocker_label"),
            ("status", "source_blocker_status"),
            ("classification", "source_blocker_classification"),
            ("detail", "source_blocker_detail"),
            ("validation_command", "source_blocker_validation_command"),
        ):
            value = str(candidate.get(source_key, "")).strip()
            if value:
                source[target_key] = value
        return source
    return None


def _summary(evidence: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "ready": sum(1 for row in evidence if row["status"] == "ready"),
        "missing": sum(1 for row in evidence if row["status"] == "missing"),
        "blocked": sum(1 for row in evidence if row["status"] == "blocked"),
        "partial": sum(1 for row in evidence if row["status"] == "partial"),
        "requires_live_provider_consent": sum(
            1 for row in evidence if row["requires_live_provider_consent"]
        ),
    }


def _overall_status(summary: dict[str, int]) -> str:
    if summary["blocked"]:
        return "blocked"
    if summary["missing"]:
        return "missing"
    if summary["partial"]:
        return "partial"
    return "ready"


def _first_blocker(evidence: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in evidence:
        if row["status"] in {"ready"}:
            continue
        return (
            {
                "id": row["id"],
                "label": row["label"],
                "status": row["status"],
                "classification": row["classification"],
                "command": row["command"],
                "detail": row["detail"],
            }
            | _source_blocker_fields(row)
            | _live_metadata_from_row(row)
        )
    return None


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    slot = _slot_by_id(str(first_blocker["id"]))
    action_command = normalize_operator_action(
        _operator_action_for_blocker(first_blocker, slot=slot)
    )
    return {
        **first_blocker,
        "command": action_command,
        "requires_live_provider_consent": slot.requires_live_provider_consent,
        "validation_command": "make live-provider-evidence",
        "source": "first_blocker",
    } | _slot_live_confirmation_metadata(slot)


def _operator_actions(
    *,
    status: str,
    evidence: list[dict[str, Any]],
    first_blocker: dict[str, Any] | None,
) -> list[str]:
    if status == "ready":
        return []
    granular_actions = _granular_live_evaluation_actions(evidence)
    if granular_actions:
        return granular_actions
    actions: list[str] = []
    if first_blocker is not None:
        slot = _slot_by_id(str(first_blocker["id"]))
        actions.append(_operator_action_for_blocker(first_blocker, slot=slot))
    else:
        actions.append("make live-provider-evidence")
    return _dedupe([normalize_operator_action(action) for action in actions])


def _granular_live_evaluation_actions(evidence: list[dict[str, Any]]) -> list[str]:
    provider_handoff = next(
        (row for row in evidence if row["id"] == "provider_handoff"),
        None,
    )
    if provider_handoff is None or provider_handoff.get("status") != "ready":
        return []
    actions: list[str] = []
    for row in evidence:
        if row["id"] not in {
            "three_d_evaluation_configured",
            "npc_evaluation_configured",
        }:
            continue
        if row.get("status") == "ready":
            continue
        slot = _slot_by_id(str(row["id"]))
        actions.append(_operator_action_for_blocker(row, slot=slot))
    return _dedupe([normalize_operator_action(action) for action in actions])


def _operator_action_for_blocker(
    first_blocker: dict[str, Any],
    *,
    slot: EvidenceSlot,
) -> str:
    command = str(first_blocker.get("command", slot.command)).strip() or slot.command
    if slot.requires_live_provider_consent:
        command = _with_live_provider_consent(command)
    source_validation = str(
        first_blocker.get("source_blocker_validation_command", "")
    ).strip()
    validations = _dedupe(
        [
            validation
            for validation in (
                source_validation,
                "make live-provider-evidence",
            )
            if validation
        ]
    )
    action = command
    for validation in validations:
        if action == validation or f"; rerun {validation}" in action:
            continue
        action += f"; rerun {validation}"
    return action


def _with_live_provider_consent(command: str) -> str:
    if command.startswith(LIVE_PROVIDER_CONSENT_ENV_PREFIX):
        return command
    return f"{LIVE_PROVIDER_CONSENT_ENV_PREFIX}{command}"


def _slot_by_id(slot_id: str) -> EvidenceSlot:
    for slot in EVIDENCE_SLOTS:
        if slot.slot_id == slot_id:
            return slot
    return EVIDENCE_SLOTS[0]


def _source_blocker_fields(row: dict[str, Any]) -> dict[str, str]:
    return {
        key: str(row[key])
        for key in (
            "source_blocker_id",
            "source_blocker_label",
            "source_blocker_status",
            "source_blocker_classification",
            "source_blocker_command",
            "source_blocker_detail",
            "source_blocker_validation_command",
        )
        if key in row and str(row[key]).strip()
    }


def _slot_live_confirmation_metadata(slot: EvidenceSlot) -> dict[str, bool]:
    if not slot.requires_live_provider_consent:
        return {}
    return {
        "requires_cost_consent": True,
        "live_provider_call": True,
        "requires_user_confirmation": True,
    }


def _live_metadata_from_row(row: dict[str, Any]) -> dict[str, bool]:
    metadata: dict[str, bool] = {}
    for key in (
        "requires_live_provider_consent",
        "requires_cost_consent",
        "live_provider_call",
        "requires_user_confirmation",
    ):
        if bool(row.get(key)):
            metadata[key] = True
    return metadata


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


def _non_negative_int(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(parsed, 0)


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
        r"sk-[A-Za-z0-9_-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Authorization\s+Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"file://[^\s,;\"']+",
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
