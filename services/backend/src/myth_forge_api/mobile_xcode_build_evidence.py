from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

SCRIPT_PATH = Path("apps/mobile/ios/scripts/xcode_build_gate.sh")
COMMAND = "make mobile-xcode-build"
EVIDENCE_COMMAND = "make mobile-xcode-build-evidence"
DERIVED_DATA_PATH = Path("apps/mobile/ios/.build/xcode-derived-data")
CommandRunner = Callable[[Path], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class MobileXcodeBuildEvidenceResult:
    exit_code: int
    report: dict[str, Any]


def run_mobile_xcode_build_evidence(
    *,
    repo_root: Path | str | None = None,
    command_runner: CommandRunner | None = None,
) -> MobileXcodeBuildEvidenceResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    runner = command_runner or _run_script
    try:
        completed = runner(selected_repo_root)
    except subprocess.TimeoutExpired as exc:
        return build_mobile_xcode_build_evidence_report(
            repo_root=selected_repo_root,
            returncode=2,
            stdout=exc.stdout if isinstance(exc.stdout, str) else "",
            stderr="mobile xcode build evidence timed out",
        )
    except OSError as exc:
        return build_mobile_xcode_build_evidence_report(
            repo_root=selected_repo_root,
            returncode=2,
            stdout="",
            stderr=f"mobile xcode build evidence could not run: {exc}",
        )
    return build_mobile_xcode_build_evidence_report(
        repo_root=selected_repo_root,
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def build_mobile_xcode_build_evidence_report(
    *,
    repo_root: Path | str | None = None,
    returncode: int,
    stdout: str,
    stderr: str,
) -> MobileXcodeBuildEvidenceResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    classification = _classification(returncode=returncode, stdout=stdout, stderr=stderr)
    status = "ready" if classification == "ready" else "blocked"
    checks = [_check_for_classification(classification)]
    actions = [] if status == "ready" else [_operator_action(classification)]
    first_blocker = _first_blocker(
        status=status,
        classification=classification,
        checks=checks,
    )
    next_action = _next_action(first_blocker)
    report = {
        "kind": "mobile_xcode_build_evidence_report",
        "status": status,
        "classification": classification,
        "command": COMMAND,
        "script": SCRIPT_PATH.as_posix(),
        "exit_code": returncode,
        "checks": checks,
        "stdout_lines": _safe_lines(stdout, repo_root=selected_repo_root),
        "stderr_lines": _safe_lines(stderr, repo_root=selected_repo_root),
        "operator_actions": actions,
        "first_blocker": first_blocker,
        "next_action": next_action,
        "device_action_bundle": _device_action_bundle(
            status=status,
            checks=checks,
            first_blocker=first_blocker,
        ),
        "safety": {
            "commands_run": True,
            "provider_calls": False,
            "live_provider_calls": False,
            "writes_backend_env": False,
            "writes_ios_deploy_config": False,
            "global_mutation": False,
            "xcode_or_signing": True,
            "code_signing_allowed": False,
            "keychain_writes": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "writes_derived_data": True,
            "derived_data_path": DERIVED_DATA_PATH.as_posix(),
        },
    }
    sanitized = _sanitize_report(report, selected_repo_root)
    return MobileXcodeBuildEvidenceResult(
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
        timeout=300,
    )


def _classification(*, returncode: int, stdout: str, stderr: str) -> str:
    output = "\n".join([stdout, stderr]).lower()
    if returncode == 0:
        return "ready"
    if (
        returncode == 127
        or "could not find xcodebuild" in output
        or "requires xcode" in output
    ):
        return "blocked_by_xcode_installation"
    if returncode == 69 or ("license" in output and "xcode" in output):
        return "blocked_by_apple_sdk_license"
    if "** build failed **" in output:
        return "xcode_project_build_failed"
    return "xcode_build_gate_failed"


def _check_for_classification(classification: str) -> dict[str, str]:
    if classification == "ready":
        return _check(
            "xcode_build_gate",
            "Xcode build gate",
            "ready",
            "Xcode build gate passed with code signing disabled.",
        )
    if classification == "blocked_by_xcode_installation":
        return _check(
            "xcode_installation",
            "Xcode installation",
            "blocked",
            "Xcode build gate could not find xcodebuild.",
        )
    if classification == "blocked_by_apple_sdk_license":
        return _check(
            "xcode_license",
            "Xcode license",
            "blocked",
            "Apple SDK license agreement is not accepted.",
        )
    if classification == "xcode_project_build_failed":
        return _check(
            "xcode_project_build",
            "Xcode project build",
            "blocked",
            "Xcode project build failed.",
        )
    return _check(
        "xcode_build_gate",
        "Xcode build gate",
        "blocked",
        "Review make mobile-xcode-build output.",
    )


def _check(check_id: str, label: str, status: str, detail: str) -> dict[str, str]:
    return {"id": check_id, "label": label, "status": status, "detail": detail}


def _first_blocker(
    *,
    status: str,
    classification: str,
    checks: list[dict[str, str]],
) -> dict[str, str] | None:
    if status == "ready":
        return None
    check = checks[0] if checks else _check(
        "xcode_build_gate",
        "Xcode build gate",
        "blocked",
        "Review make mobile-xcode-build output.",
    )
    return {
        "id": check["id"],
        "label": check["label"],
        "status": check["status"],
        "classification": classification,
        "command": _operator_action(classification),
        "detail": check["detail"],
        "validation_command": EVIDENCE_COMMAND,
    }


def _next_action(first_blocker: dict[str, str] | None) -> dict[str, str] | None:
    if first_blocker is None:
        return None
    return {**first_blocker, "source": "first_blocker"}


def _operator_action(classification: str) -> str:
    if classification == "blocked_by_xcode_installation":
        return f"install Xcode or set DEVELOPER_DIR, then rerun {EVIDENCE_COMMAND}"
    if classification == "blocked_by_apple_sdk_license":
        return f"accept the Xcode license outside Codex, then rerun {EVIDENCE_COMMAND}"
    if classification == "xcode_project_build_failed":
        return f"fix the iOS project build error, then rerun {EVIDENCE_COMMAND}"
    return f"review {COMMAND} output, then rerun {EVIDENCE_COMMAND}"


def _device_action_bundle(
    *,
    status: str,
    checks: list[dict[str, str]],
    first_blocker: dict[str, str] | None,
) -> dict[str, Any]:
    actions = [
        _device_action(check=check, first_blocker=first_blocker)
        for check in checks
    ]
    return {
        "id": "mobile_xcode_build_evidence_actions",
        "label": "Mobile Xcode Build Evidence Actions",
        "source_report": "mobile_xcode_build_evidence",
        "status": status,
        "actions": actions,
        "first_action": _first_device_action(actions),
        "summary": _device_action_summary(actions),
        "safety": _device_action_safety(),
    }


def _device_action(
    *,
    check: dict[str, str],
    first_blocker: dict[str, str] | None,
) -> dict[str, Any]:
    status = check["status"]
    matching_blocker = (
        first_blocker if _first_blocker_matches(check, first_blocker) else None
    )
    classification = str(matching_blocker.get("classification", "")) if matching_blocker else ""
    command = (
        str(matching_blocker["command"])
        if matching_blocker
        else _device_action_command(status=status, classification=classification)
    )
    is_blocked = status != "ready"
    action: dict[str, Any] = {
        "id": check["id"],
        "label": check["label"],
        "status": status,
        "classification": classification,
        "command": command,
        "detail": check.get("detail", ""),
        "manual": is_blocked,
        "provider_calls": False,
        "global_action": is_blocked,
        "xcode_or_signing": is_blocked,
    }
    if is_blocked:
        action["validation_command"] = EVIDENCE_COMMAND
        action["next_action"] = {
            "id": action["id"],
            "label": action["label"],
            "status": action["status"],
            "command": action["command"],
            "detail": action["detail"],
            "source": "device_action_bundle",
            "validation_command": EVIDENCE_COMMAND,
        }
    return action


def _first_blocker_matches(
    check: dict[str, str],
    first_blocker: dict[str, str] | None,
) -> bool:
    return first_blocker is not None and first_blocker.get("id") == check.get("id")


def _device_action_command(*, status: str, classification: str) -> str:
    if status == "ready":
        return COMMAND
    return _operator_action(classification)


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
        "xcode_or_signing": True,
        "code_signing_allowed": False,
        "keychain_writes": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
        "writes_derived_data": True,
    }


def _safe_lines(text: str, *, repo_root: Path) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = _safe_text(raw_line.strip(), repo_root)
        if line:
            lines.append(line[:240])
        if len(lines) == 12:
            break
    return lines


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
