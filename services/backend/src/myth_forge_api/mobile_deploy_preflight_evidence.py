from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from myth_forge_api.operator_actions import (
    MOBILE_WRITE_DEPLOY_CONFIG_AUTO_ACTION,
    add_mobile_deploy_validation_command,
    normalize_operator_action,
)

SCRIPT_PATH = Path("apps/mobile/ios/scripts/deploy_preflight.sh")
COMMAND = "make mobile-deploy-preflight"
CommandRunner = Callable[[Path], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class MobileDeployPreflightEvidenceResult:
    exit_code: int
    report: dict[str, Any]


def run_mobile_deploy_preflight_evidence(
    *,
    repo_root: Path | str | None = None,
    command_runner: CommandRunner | None = None,
) -> MobileDeployPreflightEvidenceResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    runner = command_runner or _run_script
    try:
        completed = runner(selected_repo_root)
    except subprocess.TimeoutExpired as exc:
        return build_mobile_deploy_preflight_evidence_report(
            repo_root=selected_repo_root,
            returncode=2,
            stdout=exc.stdout if isinstance(exc.stdout, str) else "",
            stderr="mobile deploy preflight timed out",
        )
    except OSError as exc:
        return build_mobile_deploy_preflight_evidence_report(
            repo_root=selected_repo_root,
            returncode=2,
            stdout="",
            stderr=f"mobile deploy preflight could not run: {exc}",
        )
    return build_mobile_deploy_preflight_evidence_report(
        repo_root=selected_repo_root,
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def build_mobile_deploy_preflight_evidence_report(
    *,
    repo_root: Path | str | None = None,
    returncode: int,
    stdout: str,
    stderr: str,
) -> MobileDeployPreflightEvidenceResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    status = "ready" if returncode == 0 else "blocked"
    checks = _checks(stdout=stdout, stderr=stderr, status=status)
    raw_actions = [] if status == "ready" else _operator_actions(checks)
    actions = [_validation_aware_action(action) for action in raw_actions]
    first_blocker = _first_blocker(checks)
    next_action = _next_action(first_blocker, raw_actions, checks)
    report = {
        "kind": "mobile_deploy_preflight_evidence_report",
        "status": status,
        "first_blocker": first_blocker,
        "next_action": next_action,
        "command": COMMAND,
        "script": SCRIPT_PATH.as_posix(),
        "exit_code": returncode,
        "checks": checks,
        "stdout_lines": _safe_lines(stdout, repo_root=selected_repo_root),
        "stderr_lines": _safe_lines(stderr, repo_root=selected_repo_root),
        "operator_actions": actions,
        "device_action_bundle": _device_action_bundle(
            status=status,
            checks=checks,
            raw_actions=raw_actions,
            next_action=next_action,
        ),
        "safety": {
            "commands_run": True,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "global_mutation": False,
            "xcode_or_signing": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
        },
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return MobileDeployPreflightEvidenceResult(
        exit_code=0 if sanitized["status"] == "ready" else 2,
        report=sanitized,
    )


def _run_script(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", SCRIPT_PATH.as_posix()],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


def _checks(*, stdout: str, stderr: str, status: str) -> list[dict[str, str]]:
    output = "\n".join([stdout, stderr])
    checks: list[dict[str, str]] = []
    if "Missing DEVELOPMENT_TEAM" in output:
        checks.append(
            _check("development_team", "Apple Team ID", "blocked", "Missing DEVELOPMENT_TEAM")
        )
    if "Missing PRODUCT_BUNDLE_IDENTIFIER" in output:
        checks.append(
            _check(
                "bundle_identifier",
                "Bundle identifier",
                "blocked",
                "Missing PRODUCT_BUNDLE_IDENTIFIER",
            )
        )
    if "Missing PMF_BACKEND_BASE_URL" in output:
        checks.append(
            _check(
                "backend_base_url",
                "Backend base URL",
                "blocked",
                "Missing PMF_BACKEND_BASE_URL",
            )
        )
    if "not loopback" in output:
        checks.append(
            _check(
                "backend_base_url",
                "Backend base URL",
                "blocked",
                "PMF_BACKEND_BASE_URL must be iPhone-reachable",
            )
        )
    if "PMF_FINAL_LAUNCH_MODE must be local or configured" in output:
        checks.append(
            _check(
                "final_launch_mode",
                "Final launch mode",
                "blocked",
                "PMF_FINAL_LAUNCH_MODE must be local or configured",
            )
        )
    if "Backend health check failed" in output:
        checks.append(
            _check("backend_health", "Backend health", "blocked", "Backend health check failed")
        )
    if "Deployment.local.xcconfig must stay untracked" in output:
        checks.append(
            _check(
                "deploy_config_tracking",
                "Deploy config tracking",
                "blocked",
                "Deployment.local.xcconfig must stay untracked",
            )
        )
    if status == "ready":
        checks.append(
            _check(
                "deploy_preflight",
                "iOS deploy preflight",
                "ready",
                "iOS deploy preflight passed.",
            )
        )
        if "Backend health: ok" in output:
            checks.append(
                _check("backend_health", "Backend health", "ready", "Backend health: ok")
            )
        if "Final launch mode:" in output:
            checks.append(
                _check(
                    "final_launch_mode",
                    "Final launch mode",
                    "ready",
                    _line_containing(output, "Final launch mode:"),
                )
            )
    if not checks:
        checks.append(
            _check(
                "deploy_preflight",
                "iOS deploy preflight",
                status,
                "review make mobile-deploy-preflight output",
            )
        )
    return _dedupe_checks(checks)


def _check(check_id: str, label: str, status: str, detail: str) -> dict[str, str]:
    return {"id": check_id, "label": label, "status": status, "detail": detail}


def _first_blocker(checks: list[dict[str, str]]) -> dict[str, str] | None:
    for check in checks:
        if check.get("status") != "ready":
            return {
                "id": check["id"],
                "label": check["label"],
                "status": check["status"],
                "detail": check["detail"],
            }
    return None


def _next_action(
    first_blocker: dict[str, str] | None,
    actions: list[str],
    checks: list[dict[str, str]],
) -> dict[str, str] | None:
    if first_blocker is None:
        return None
    command = _validation_aware_action(actions[0]) if actions else first_blocker["detail"]
    detail = _blocked_check_detail_summary(checks) or first_blocker["detail"]
    return {
        "id": first_blocker["id"],
        "label": first_blocker["label"],
        "status": first_blocker["status"],
        "command": command,
        "detail": detail,
        "validation_command": COMMAND,
        "source": "first_blocker",
    }


def _blocked_check_detail_summary(checks: list[dict[str, str]]) -> str:
    details: list[str] = []
    seen: set[str] = set()
    for check in checks:
        if check.get("status") == "ready":
            continue
        detail = check.get("detail", "").strip()
        if not detail or detail in seen:
            continue
        seen.add(detail)
        details.append(detail)
    return "; ".join(details)


def _operator_actions(checks: list[dict[str, str]]) -> list[str]:
    actions: list[str] = []
    blocked_ids = {
        check["id"] for check in checks if check.get("status") != "ready"
    }
    if (
        "development_team" in blocked_ids
        and "backend_base_url" in blocked_ids
        and "bundle_identifier" not in blocked_ids
    ):
        actions.append(MOBILE_WRITE_DEPLOY_CONFIG_AUTO_ACTION)
    for check in checks:
        check_id = check["id"]
        if check_id in {"development_team", "backend_base_url"} and (
            MOBILE_WRITE_DEPLOY_CONFIG_AUTO_ACTION in actions
        ):
            continue
        if check_id == "development_team":
            actions.append("provide DEVELOPMENT_TEAM in Deployment.local.xcconfig")
        elif check_id == "bundle_identifier":
            actions.append("provide PRODUCT_BUNDLE_IDENTIFIER in Deployment.local.xcconfig")
        elif check_id == "backend_base_url":
            actions.append("set PMF_BACKEND_BASE_URL to an iPhone-reachable LAN URL")
        elif check_id == "final_launch_mode":
            actions.append("set PMF_FINAL_LAUNCH_MODE to local or configured")
        elif check_id == "backend_health":
            actions.append("start backend-device-demo and rerun mobile deploy preflight")
        elif check_id == "deploy_config_tracking":
            actions.append("remove Deployment.local.xcconfig from git tracking")
        else:
            actions.append("review make mobile-deploy-preflight output")
    return _dedupe(actions)


def _device_action_bundle(
    *,
    status: str,
    checks: list[dict[str, str]],
    raw_actions: list[str],
    next_action: dict[str, str] | None,
) -> dict[str, Any]:
    actions = [
        _device_action(
            check=check,
            index=index,
            raw_actions=raw_actions,
            report_next_action=next_action,
        )
        for index, check in enumerate(checks)
    ]
    return {
        "id": "mobile_deploy_preflight_evidence_actions",
        "label": "Mobile Deploy Preflight Evidence Actions",
        "source_report": "mobile_deploy_preflight_evidence",
        "status": status,
        "actions": actions,
        "first_action": _first_device_action(actions),
        "summary": _device_action_summary(actions),
        "safety": _device_action_safety(),
    }


def _device_action(
    *,
    check: dict[str, str],
    index: int,
    raw_actions: list[str],
    report_next_action: dict[str, str] | None,
) -> dict[str, Any]:
    status = check["status"]
    command = _device_action_command(
        check=check,
        index=index,
        raw_actions=raw_actions,
        report_next_action=report_next_action,
    )
    action: dict[str, Any] = {
        "id": check["id"],
        "label": check["label"],
        "status": status,
        "classification": "",
        "command": command,
        "detail": check.get("detail", ""),
        "manual": status != "ready",
        "provider_calls": False,
        "global_action": False,
        "xcode_or_signing": False,
    }
    if status != "ready":
        action["validation_command"] = COMMAND
        action["next_action"] = {
            "id": action["id"],
            "label": action["label"],
            "status": action["status"],
            "command": action["command"],
            "detail": action["detail"],
            "source": "device_action_bundle",
            "validation_command": COMMAND,
        }
    return action


def _device_action_command(
    *,
    check: dict[str, str],
    index: int,
    raw_actions: list[str],
    report_next_action: dict[str, str] | None,
) -> str:
    if (
        report_next_action is not None
        and report_next_action.get("id") == check.get("id")
    ):
        return report_next_action["command"]
    if check.get("status") == "ready":
        return COMMAND
    raw_action = _raw_action_for_check(
        check=check,
        index=index,
        raw_actions=raw_actions,
    )
    if raw_action is not None:
        return _validation_aware_action(raw_action)
    return check.get("detail", "review make mobile-deploy-preflight output")


def _raw_action_for_check(
    *,
    check: dict[str, str],
    index: int,
    raw_actions: list[str],
) -> str | None:
    if (
        check.get("id") == "backend_base_url"
        and MOBILE_WRITE_DEPLOY_CONFIG_AUTO_ACTION in raw_actions
    ):
        return MOBILE_WRITE_DEPLOY_CONFIG_AUTO_ACTION
    if index < len(raw_actions):
        return raw_actions[index]
    return None


def _first_device_action(actions: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((action for action in actions if action["status"] != "ready"), None)


def _device_action_summary(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actions": len(actions),
        "ready": sum(1 for action in actions if action["status"] == "ready"),
        "missing": sum(1 for action in actions if action["status"] == "missing"),
        "blocked": sum(1 for action in actions if action["status"] == "blocked"),
        "manual": sum(1 for action in actions if action.get("manual") is True),
        "provider_calls": sum(1 for action in actions if action["provider_calls"] is True),
        "global_actions": sum(1 for action in actions if action["global_action"] is True),
        "xcode_or_signing": sum(
            1 for action in actions if action["xcode_or_signing"] is True
        ),
    }


def _device_action_safety() -> dict[str, bool]:
    return {
        "commands_run": True,
        "provider_calls": False,
        "live_provider_calls": False,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "global_mutation": False,
        "xcode_or_signing": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
    }


def _validation_aware_action(action: str) -> str:
    return add_mobile_deploy_validation_command(normalize_operator_action(action))


def _safe_lines(text: str, *, repo_root: Path) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = _safe_text(raw_line.strip(), repo_root)
        if line:
            lines.append(line[:240])
        if len(lines) == 12:
            break
    return lines


def _line_containing(text: str, needle: str) -> str:
    for line in text.splitlines():
        if needle in line:
            return line.strip()
    return needle


def _dedupe_checks(checks: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for check in checks:
        key = check["id"]
        if key in seen:
            continue
        seen.add(key)
        result.append(check)
    return result


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
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"local-capture://[^\s,;\"']+",
        r"file://[^\s,;\"']+",
        r"https?://pay\.[^\s,;\"']+",
        r"https?://checkout\.[^\s,;\"']+",
        r"checkout_url",
        r"raw_email:[^\n\r]+",
        r"raw_calendar:[^\n\r]+",
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


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
