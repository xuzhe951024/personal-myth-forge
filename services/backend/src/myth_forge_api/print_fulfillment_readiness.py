from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from myth_forge_api.config import Settings, load_settings
from myth_forge_api.domain.models import PrintQuoteRequest
from myth_forge_api.final_resources_preflight import (
    build_final_resources_preflight_report,
)
from myth_forge_api.ios_showcase_acceptance import run_ios_showcase_acceptance
from myth_forge_api.print_acceptance import run_print_quote_acceptance
from myth_forge_api.resource_handoff import build_resource_handoff_report
from myth_forge_api.visual_regression_readiness import (
    build_visual_regression_readiness_report,
)

CONFIGURED_PRINT_QUOTE_PATH = Path("services/backend/.local/print-quote-configured.json")
CONFIGURED_PRINT_QUOTE_REQUEST_PATH = Path(
    "services/backend/.local/print-quote-request-configured.json"
)
FINAL_DEMO_LAUNCH_LOCAL_PATH = Path("services/backend/.local/final-demo-launch-local.json")
IOS_DEPLOY_CONFIG_PATH = Path("apps/mobile/ios/Config/Deployment.local.xcconfig")
FINAL_DEMO_LAUNCH_LOCAL_COMMAND = "make final-demo-launch-local"
IPHONE_BACKEND_URL_ACTION = "set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL"
PRINT_RECEIPT_ARTIFACT_ID = "p0.101_print_fulfillment_receipt"
PRINT_SOURCE_FEATURE_ID = "mobile_print_fulfillment_receipt"


@dataclass(frozen=True)
class PrintFulfillmentReadinessResult:
    exit_code: int
    report: dict[str, Any]


def build_print_fulfillment_readiness_report(
    *,
    settings: Settings | None = None,
    repo_root: Path | str | None = None,
) -> PrintFulfillmentReadinessResult:
    selected_settings = settings or load_settings()
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    print_acceptance = run_print_quote_acceptance().report
    source_acceptance = run_ios_showcase_acceptance(repo_root=selected_repo_root).report
    visual_regression = build_visual_regression_readiness_report(
        repo_root=selected_repo_root,
    ).report
    final_resources = build_final_resources_preflight_report(
        repo_root=selected_repo_root,
    ).report
    resource_handoff = build_resource_handoff_report(
        settings=selected_settings,
        repo_root=selected_repo_root,
    )
    configured_quote = _read_configured_treatstock_quote(selected_repo_root)
    configured_quote_request = _read_configured_treatstock_quote_request(
        repo_root=selected_repo_root,
        configured_quote=configured_quote,
    )
    checks = [
        _print_quote_acceptance_check(print_acceptance),
        _source_acceptance_check(source_acceptance),
        _visual_print_receipt_check(visual_regression),
        _print_resource_handoff_check(
            final_resources=final_resources,
            resource_handoff=resource_handoff,
            settings=selected_settings,
        ),
        _configured_treatstock_quote_request_check(
            configured_quote_request,
            repo_root=selected_repo_root,
        ),
        _configured_treatstock_quote_check(configured_quote),
    ]
    summary = _summary(checks)
    status = _overall_status(checks)
    first_blocker = _first_blocker(checks)
    report = {
        "kind": "print_fulfillment_readiness_report",
        "status": status,
        "summary": summary,
        "checks": checks,
        "checks_by_id": {check["id"]: check for check in checks},
        "first_blocker": first_blocker,
        "next_action": _next_action(first_blocker),
        "operator_actions": _operator_actions(checks),
        "commands": _commands(),
        "evidence": {
            "print_quote_acceptance": _evidence_summary(print_acceptance),
            "ios_showcase_acceptance": _evidence_summary(source_acceptance),
            "visual_regression_readiness": _evidence_summary(visual_regression),
            "final_resources_preflight": _evidence_summary(final_resources),
            "resource_handoff": _evidence_summary(resource_handoff),
            "configured_treatstock_quote_request": configured_quote_request["summary"],
            "configured_treatstock_quote": configured_quote["summary"],
        },
        "safety": {
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
        },
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return PrintFulfillmentReadinessResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _print_quote_acceptance_check(report: dict[str, Any]) -> dict[str, Any]:
    if report.get("status") == "succeeded" and report.get("quote_status") == "draft_quote":
        return _check(
            check_id="print_quote_acceptance",
            label="Local print quote acceptance",
            status="ready",
            classification="local_draft_quote_ready",
            command="cd services/backend && uv run pytest tests/test_print_acceptance.py",
            detail="Deterministic local print candidate and draft quote are ready.",
            evidence=[
                f"provider:{report.get('provider', 'unknown')}",
                f"format:{report.get('candidate_format', 'unknown')}",
                f"requires_user_approval:{report.get('requires_user_approval', False)}",
            ],
        )
    return _check(
        check_id="print_quote_acceptance",
        label="Local print quote acceptance",
        status="blocked",
        classification="local_print_quote_failed",
        command="cd services/backend && uv run pytest tests/test_print_acceptance.py",
        detail=str(report.get("error") or "Local print quote acceptance is not ready."),
        evidence=[f"status:{report.get('status', 'unknown')}"],
    )


def _source_acceptance_check(report: dict[str, Any]) -> dict[str, Any]:
    feature = _feature_by_id(report, PRINT_SOURCE_FEATURE_ID)
    if feature is not None and feature.get("status") == "passed":
        return _check(
            check_id="ios_print_fulfillment_source",
            label="iPhone print fulfillment source",
            status="ready",
            classification="source_acceptance_passed",
            command="cd services/backend && uv run pytest tests/test_ios_showcase_acceptance.py",
            detail="iPhone source acceptance covers print fulfillment receipt and approval gate.",
            evidence=[f"feature:{PRINT_SOURCE_FEATURE_ID}"],
        )
    missing = feature.get("missing", []) if isinstance(feature, dict) else []
    return _check(
        check_id="ios_print_fulfillment_source",
        label="iPhone print fulfillment source",
        status="blocked",
        classification="missing_source_acceptance",
        command="cd services/backend && uv run pytest tests/test_ios_showcase_acceptance.py",
        detail=_missing_source_detail(missing),
        evidence=[f"feature:{PRINT_SOURCE_FEATURE_ID}"],
    )


def _visual_print_receipt_check(report: dict[str, Any]) -> dict[str, Any]:
    artifact = _artifact_by_id(report, PRINT_RECEIPT_ARTIFACT_ID)
    report_status = _normalized_status(str(report.get("status", "missing")))
    if (
        report_status == "ready"
        and artifact is not None
        and artifact.get("status") == "passed"
    ):
        return _check(
            check_id="visual_print_receipt",
            label="Print fulfillment visual regression",
            status="ready",
            classification="artifact_ready",
            command="make visual-regression-local",
            detail="Print fulfillment receipt visual artifact is present and passed.",
            evidence=[f"artifact:{PRINT_RECEIPT_ARTIFACT_ID}"],
        )
    classification = "missing_visual_artifact"
    detail = "Print fulfillment visual artifact is missing or not passed."
    if report_status == "blocked":
        classification = _first_blocker_classification(report, default="visual_report_blocked")
        detail = _first_blocker_detail(report, default=detail)
    return _check(
        check_id="visual_print_receipt",
        label="Print fulfillment visual regression",
        status="blocked",
        classification=classification,
        command="make visual-regression-local",
        detail=detail,
        evidence=[
            f"visual_regression_readiness:{report.get('status', 'unknown')}",
            f"artifact:{PRINT_RECEIPT_ARTIFACT_ID}",
        ],
    )


def _print_resource_handoff_check(
    *,
    final_resources: dict[str, Any],
    resource_handoff: dict[str, Any],
    settings: Settings,
) -> dict[str, Any]:
    final_resource_items = _items_by_id(final_resources.get("items", []))
    resource_items = _items_by_id(resource_handoff.get("backend", {}).get("items", []))
    print_provider_statuses = [
        _item_status(final_resource_items, "PRINT_PROVIDER"),
        _item_status(resource_items, "PRINT_PROVIDER"),
    ]
    treatstock_statuses: list[str] = []
    if settings.print_provider == "treatstock":
        treatstock_statuses = [
            _item_status(final_resource_items, "TREATSTOCK_API_KEY"),
            _item_status(resource_items, "TREATSTOCK_API_KEY"),
        ]
    statuses = print_provider_statuses + treatstock_statuses
    if statuses and all(status in {"ready", "optional"} for status in statuses):
        return _check(
            check_id="print_resource_handoff",
            label="Print provider resource handoff",
            status="ready",
            classification="print_resources_ready",
            command="make final-resources-preflight",
            detail="Print provider selection and required Treatstock key handoff are ready.",
            evidence=[
                f"print_provider:{settings.print_provider}",
                f"final_resources:{final_resources.get('status', 'unknown')}",
                f"resource_handoff:{resource_handoff.get('overall_status', 'unknown')}",
            ],
        )
    return _check(
        check_id="print_resource_handoff",
        label="Print provider resource handoff",
        status="blocked",
        classification="print_resource_handoff_incomplete",
        command="make final-resources-preflight",
        detail="Print provider resources must include PRINT_PROVIDER and required Treatstock key state.",
        evidence=[
            f"print_provider:{settings.print_provider}",
            f"statuses:{','.join(statuses) if statuses else 'missing'}",
        ],
    )


def _configured_treatstock_quote_check(configured_quote: dict[str, Any]) -> dict[str, Any]:
    if not configured_quote["exists"]:
        return _check(
            check_id="configured_treatstock_quote",
            label="Configured Treatstock quote",
            status="partial",
            classification="missing_configured_treatstock_quote",
            command=_configured_quote_command(),
            detail="Local print proof is ready; configured Treatstock quote evidence is not present.",
            evidence=[f"path:{CONFIGURED_PRINT_QUOTE_PATH.as_posix()}"],
        )
    if configured_quote["status"] != "ready":
        return _check(
            check_id="configured_treatstock_quote",
            label="Configured Treatstock quote",
            status="blocked",
            classification=str(configured_quote["classification"]),
            command=_configured_quote_command(),
            detail=str(configured_quote["detail"]),
            evidence=[f"path:{CONFIGURED_PRINT_QUOTE_PATH.as_posix()}"],
        )
    summary = configured_quote["summary"]
    return _check(
        check_id="configured_treatstock_quote",
        label="Configured Treatstock quote",
        status="ready",
        classification="draft_quote_requires_user_approval",
        command=_configured_quote_command(),
        detail=(
            "Configured Treatstock draft quote is ready and still requires explicit user approval."
        ),
        evidence=[
            f"provider:{summary.get('provider', 'unknown')}",
            f"currency:{summary.get('currency', 'unknown')}",
            f"estimated_price_cents:{summary.get('estimated_price_cents', 'unknown')}",
        ],
    )


def _configured_treatstock_quote_request_check(
    configured_quote_request: dict[str, Any],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    if configured_quote_request["status"] != "ready":
        return _check(
            check_id="configured_treatstock_quote_request",
            label="Configured Treatstock quote request",
            status="blocked",
            classification=str(configured_quote_request["classification"]),
            command=_configured_quote_request_command(repo_root=repo_root),
            detail=str(configured_quote_request["detail"]),
            evidence=[f"path:{CONFIGURED_PRINT_QUOTE_REQUEST_PATH.as_posix()}"],
        )
    return _check(
        check_id="configured_treatstock_quote_request",
        label="Configured Treatstock quote request",
        status="ready",
        classification=str(configured_quote_request["classification"]),
        command=_configured_quote_command(),
        detail=str(configured_quote_request["detail"]),
        evidence=[f"path:{CONFIGURED_PRINT_QUOTE_REQUEST_PATH.as_posix()}"],
    )


def _read_configured_treatstock_quote_request(
    *,
    repo_root: Path,
    configured_quote: dict[str, Any],
) -> dict[str, Any]:
    path = repo_root / CONFIGURED_PRINT_QUOTE_REQUEST_PATH
    base = {
        "exists": path.exists(),
        "path": CONFIGURED_PRINT_QUOTE_REQUEST_PATH.as_posix(),
        "summary": {
            "path": CONFIGURED_PRINT_QUOTE_REQUEST_PATH.as_posix(),
            "exists": path.exists(),
        },
    }
    if configured_quote["exists"]:
        return base | {
            "status": "ready",
            "classification": "configured_quote_evidence_present",
            "detail": "Configured Treatstock quote evidence is present.",
        }
    if not path.exists():
        handoff_state = _local_print_request_handoff_state(repo_root)
        if handoff_state["status"] != "ready":
            return base | {
                "status": "blocked",
                "classification": handoff_state["classification"],
                "detail": handoff_state["detail"],
            }
        return base | {
            "status": "blocked",
            "classification": "missing_configured_treatstock_quote_request",
            "detail": (
                "Configured Treatstock quote request file is missing; local served "
                "asset URLs are ready for the request writer."
            ),
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return base | {
            "status": "blocked",
            "classification": "unreadable_quote_request_file",
            "detail": "Configured Treatstock quote request is not valid JSON.",
        }
    if not isinstance(payload, dict):
        return base | {
            "status": "blocked",
            "classification": "invalid_quote_request_shape",
            "detail": "Configured Treatstock quote request must be a JSON object.",
        }
    try:
        request = PrintQuoteRequest.model_validate(payload)
    except ValidationError:
        return base | {
            "status": "blocked",
            "classification": "invalid_quote_request_contract",
            "detail": "Configured Treatstock quote request must satisfy PrintQuoteRequest.",
        }
    summary = base["summary"] | {
        "quantity": request.quantity,
        "material": request.material,
        "finish": request.finish,
        "ship_to_country": request.ship_to_country,
        "print_candidate_format": request.print_candidate.format,
        "requires_user_approval": request.print_candidate.requires_user_approval,
    }
    return base | {
        "status": "ready",
        "classification": "configured_quote_request_ready",
        "detail": "Configured Treatstock quote request is ready for guarded quote handoff.",
        "summary": summary,
    }


def _read_configured_treatstock_quote(repo_root: Path) -> dict[str, Any]:
    path = repo_root / CONFIGURED_PRINT_QUOTE_PATH
    base = {
        "exists": path.exists(),
        "path": CONFIGURED_PRINT_QUOTE_PATH.as_posix(),
        "summary": {
            "path": CONFIGURED_PRINT_QUOTE_PATH.as_posix(),
            "exists": path.exists(),
        },
    }
    if not path.exists():
        return base | {
            "status": "partial",
            "classification": "missing_configured_treatstock_quote",
            "detail": "Configured Treatstock quote evidence file is missing.",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return base | {
            "status": "blocked",
            "classification": "unreadable_quote_file",
            "detail": "Configured Treatstock quote evidence is not valid JSON.",
        }
    if not isinstance(payload, dict):
        return base | {
            "status": "blocked",
            "classification": "invalid_quote_shape",
            "detail": "Configured Treatstock quote evidence must be a JSON object.",
        }
    summary = {
        "path": CONFIGURED_PRINT_QUOTE_PATH.as_posix(),
        "exists": True,
        "kind": payload.get("kind"),
        "provider": payload.get("provider"),
        "status": payload.get("status"),
        "currency": payload.get("currency"),
        "estimated_price_cents": payload.get("estimated_price_cents"),
        "requires_user_approval": payload.get("requires_user_approval"),
    }
    validation = _validate_configured_quote(payload)
    return base | validation | {"summary": summary}


def _validate_configured_quote(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("kind") != "print_quote":
        return _quote_blocker("wrong_quote_kind", "Configured evidence must be a print_quote.")
    if payload.get("provider") != "treatstock":
        return _quote_blocker("wrong_quote_provider", "Configured quote must come from Treatstock.")
    if payload.get("status") != "draft_quote":
        return _quote_blocker("wrong_quote_status", "Configured quote must remain a draft_quote.")
    if payload.get("requires_user_approval") is not True:
        return _quote_blocker(
            "missing_user_approval_gate",
            "Treatstock quote evidence must require explicit user approval.",
        )
    if _non_negative_int(payload.get("estimated_price_cents")) <= 0:
        return _quote_blocker(
            "missing_quote_price",
            "Treatstock quote evidence must include a positive estimated price.",
        )
    return {
        "status": "ready",
        "classification": "draft_quote_requires_user_approval",
        "detail": "Configured Treatstock draft quote is review-only.",
    }


def _quote_blocker(classification: str, detail: str) -> dict[str, Any]:
    return {"status": "blocked", "classification": classification, "detail": detail}


def _feature_by_id(report: dict[str, Any], feature_id: str) -> dict[str, Any] | None:
    features = report.get("required_features")
    if not isinstance(features, list):
        return None
    for feature in features:
        if isinstance(feature, dict) and feature.get("id") == feature_id:
            return feature
    return None


def _artifact_by_id(report: dict[str, Any], artifact_id: str) -> dict[str, Any] | None:
    artifacts = report.get("artifacts")
    if not isinstance(artifacts, list):
        return None
    for artifact in artifacts:
        if isinstance(artifact, dict) and artifact.get("id") == artifact_id:
            return artifact
    return None


def _items_by_id(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        str(item["id"]): item
        for item in items
        if isinstance(item, dict) and item.get("id") is not None
    }


def _item_status(items: dict[str, dict[str, Any]], item_id: str) -> str:
    item = items.get(item_id)
    if not item:
        return "missing"
    return str(item.get("status", "missing"))


def _missing_source_detail(missing: Any) -> str:
    if isinstance(missing, list) and missing:
        first = missing[0]
        if isinstance(first, dict):
            return (
                "Missing source requirement "
                f"{first.get('file', 'unknown_file')}::{first.get('contains', 'unknown_text')}."
            )
    return "Print fulfillment source acceptance did not pass."


def _first_blocker_classification(report: dict[str, Any], *, default: str) -> str:
    blocker = _first_report_blocker(report)
    if blocker is None:
        return default
    return str(blocker.get("classification", default))


def _first_blocker_detail(report: dict[str, Any], *, default: str) -> str:
    blocker = _first_report_blocker(report)
    if blocker is None:
        return default
    return str(blocker.get("detail", default))


def _first_report_blocker(report: dict[str, Any]) -> dict[str, Any] | None:
    blockers = report.get("blockers")
    if not isinstance(blockers, list):
        return None
    for blocker in blockers:
        if isinstance(blocker, dict):
            return blocker
    return None


def _check(
    *,
    check_id: str,
    label: str,
    status: str,
    classification: str,
    command: str,
    detail: str,
    evidence: list[str],
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": _normalized_status(status),
        "classification": classification,
        "command": command,
        "detail": detail,
        "evidence": evidence,
    }


def _summary(checks: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "ready": sum(1 for check in checks if check["status"] == "ready"),
        "partial": sum(1 for check in checks if check["status"] == "partial"),
        "blocked": sum(1 for check in checks if check["status"] == "blocked"),
    }


def _overall_status(checks: list[dict[str, Any]]) -> str:
    if any(check["status"] == "blocked" for check in checks):
        return "blocked"
    if any(check["status"] == "partial" for check in checks):
        return "partial"
    return "ready"


def _first_blocker(checks: list[dict[str, Any]]) -> dict[str, Any] | None:
    for status in ("blocked", "partial"):
        for check in checks:
            if check["status"] == status:
                return {
                    "id": check["id"],
                    "label": check["label"],
                    "status": check["status"],
                    "classification": check["classification"],
                    "command": check["command"],
                    "detail": check["detail"],
                }
    return None


def _next_action(first_blocker: dict[str, Any] | None) -> dict[str, Any] | None:
    if first_blocker is None:
        return None
    return {
        **first_blocker,
        "source": "first_blocker",
        "validation_command": "make print-fulfillment-readiness",
        "requires_cost_consent": (
            first_blocker.get("id") == "configured_treatstock_quote"
            and first_blocker.get("classification")
            == "missing_configured_treatstock_quote"
        ),
    }


def _operator_actions(checks: list[dict[str, Any]]) -> list[str]:
    validation_command = "make print-fulfillment-readiness"
    actions = [
        f"{check['command']}; rerun {validation_command}"
        for check in checks
        if check.get("status") != "ready"
    ]
    if not actions:
        actions.append(validation_command)
    return _dedupe(actions)[:8]


def _commands() -> list[str]:
    return [
        "make print-fulfillment-readiness",
        (
            "cd services/backend && uv run python -m myth_forge_api.cli "
            "print-fulfillment-readiness --repo-root ../.. "
            "--output .local/print-fulfillment-readiness.json"
        ),
        _configured_quote_request_command(),
        _configured_quote_command(),
    ]


def _configured_quote_request_command(*, repo_root: Path | None = None) -> str:
    handoff = (
        _local_print_request_handoff_state(repo_root)
        if repo_root is not None
        else {"status": "unknown"}
    )
    if handoff["status"] == "ready":
        return (
            f"PRINT_SOURCE_ASSET_URI={handoff['source_asset_uri']} "
            f"PRINT_CANDIDATE_URI={handoff['print_candidate_uri']} "
            "make print-quote-request-configured"
        )
    if handoff["status"] == "blocked":
        return str(handoff["command"])
    return (
        "PRINT_SOURCE_ASSET_URI=auto PRINT_CANDIDATE_URI=auto "
        "make print-quote-request-configured"
    )


def _local_print_request_handoff(repo_root: Path) -> dict[str, str] | None:
    handoff = _local_print_request_handoff_state(repo_root)
    if handoff["status"] != "ready":
        return None
    return {
        "source_asset_uri": str(handoff["source_asset_uri"]),
        "print_candidate_uri": str(handoff["print_candidate_uri"]),
    }


def _local_print_request_handoff_state(repo_root: Path) -> dict[str, Any]:
    session_id = _local_showcase_session_id(repo_root)
    backend_base_url = _deploy_backend_base_url(repo_root)
    if not session_id:
        return {
            "status": "blocked",
            "classification": "missing_local_demo_session_for_print_quote_request",
            "command": FINAL_DEMO_LAUNCH_LOCAL_COMMAND,
            "detail": (
                "Auto print quote request needs local final demo launch session evidence."
            ),
        }
    if not _is_iphone_reachable_http_url(backend_base_url):
        return {
            "status": "blocked",
            "classification": (
                "missing_iphone_reachable_backend_url_for_print_quote_request"
            ),
            "command": IPHONE_BACKEND_URL_ACTION,
            "detail": (
                "Auto print quote request needs an iPhone-reachable "
                "PMF_BACKEND_BASE_URL in Deployment.local.xcconfig."
            ),
        }
    base_url = backend_base_url.rstrip("/")
    return {
        "status": "ready",
        "source_asset_uri": f"{base_url}/v1/generated-assets/{session_id}/game.glb",
        "print_candidate_uri": f"{base_url}/v1/print-candidates/{session_id}/print.3mf",
    }


def _local_showcase_session_id(repo_root: Path) -> str:
    payload = _read_json_object(repo_root / FINAL_DEMO_LAUNCH_LOCAL_PATH)
    smoke = payload.get("local_showcase_smoke")
    if not isinstance(smoke, dict):
        source_reports = payload.get("source_reports")
        smoke = (
            source_reports.get("local_showcase_smoke")
            if isinstance(source_reports, dict)
            else None
        )
    session = smoke.get("session") if isinstance(smoke, dict) else None
    session_id = session.get("session_id") if isinstance(session, dict) else None
    return str(session_id).strip() if session_id else ""


def _deploy_backend_base_url(repo_root: Path) -> str:
    path = repo_root / IOS_DEPLOY_CONFIG_PATH
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return ""
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "PMF_BACKEND_BASE_URL":
            return value.strip()
    return ""


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _is_iphone_reachable_http_url(value: str) -> bool:
    lowered = value.lower()
    return (
        (lowered.startswith("http://") or lowered.startswith("https://"))
        and "://127.0.0.1" not in lowered
        and "://localhost" not in lowered
    )


def _configured_quote_command() -> str:
    return "PMF_ALLOW_PRINT_PROVIDER_CALLS=1 make print-quote-configured"


def _evidence_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "kind": report.get("kind"),
        "status": report.get("status", report.get("overall_status")),
    }
    raw_summary = report.get("summary")
    if isinstance(raw_summary, dict):
        summary["summary"] = {
            str(key): value
            for key, value in raw_summary.items()
            if isinstance(value, (int, str, bool)) or value is None
        }
    return summary


def _normalized_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in {"ready", "passed", "succeeded", "ok"}:
        return "ready"
    if normalized in {"partial", "manual", "optional", "waiting", "missing"}:
        return "partial"
    return "blocked"


def _non_negative_int(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(parsed, 0)


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    text = json.dumps(report, sort_keys=True)
    sanitized = text
    replacements = [
        (re.escape(str(repo_root)), "[repo]"),
        (r"/Users/[^\s,;\"']+", "[home]"),
        (r"/tmp/[^\s,;\"']+", "[tmp]"),
        (r"sk-[A-Za-z0-9._-]+", "[redacted]"),
        (r"Bearer\s+[A-Za-z0-9._~+/=:\-]+", "Bearer [redacted]"),
        (r"api[_-]?key\s*[=:]\s*[^\s,;\"']+", "api_key=[redacted]"),
        (r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+", "[redacted]"),
        (r"file://[^\s,;\"']+", "file://[redacted]"),
        (r"https?://checkout\.[^\s,;\"']+", "[redacted-payment-link]"),
        (r"https?://pay\.[^\s,;\"']+", "[redacted-payment-link]"),
    ]
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return json.loads(sanitized)


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
