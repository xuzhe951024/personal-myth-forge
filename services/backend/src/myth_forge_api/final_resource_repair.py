from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any

from myth_forge_api.final_resources_preflight import DEFAULT_RESOURCES_PATH

EXAMPLE_BACKEND_BASE_URLS = {"http://192.168.1.10:8080"}
REPAIRABLE_KEYS = {"PRODUCT_BUNDLE_IDENTIFIER", "PMF_BACKEND_BASE_URL"}


@dataclass(frozen=True)
class FinalResourceRepairResult:
    exit_code: int
    report: dict[str, Any]


def build_final_resource_repair_report(
    *,
    repo_root: Path | str | None = None,
    resources_file: Path | str | None = None,
    apply: bool = False,
) -> FinalResourceRepairResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    selected_resources_file = (
        Path(resources_file)
        if resources_file is not None
        else selected_repo_root / DEFAULT_RESOURCES_PATH
    )
    resources_label = _path_label(
        path=selected_resources_file,
        repo_root=selected_repo_root,
    )

    if not selected_resources_file.exists():
        report = {
            "kind": "final_resource_repair_report",
            "status": "missing",
            "resources_file": {"path": resources_label, "exists": False},
            "repairs": [],
            "operator_actions": ["run make final-resource-init"],
            "safety": _safety(writes_final_resources=False),
        }
        return FinalResourceRepairResult(exit_code=2, report=report)

    text = selected_resources_file.read_text(encoding="utf-8")
    repairs = _repairs_for_text(text)
    if repairs:
        if apply:
            tracked = _is_tracked_final_resources(
                repo_root=selected_repo_root,
                resources_file=selected_resources_file,
            )
            if tracked:
                report = {
                    "kind": "final_resource_repair_report",
                    "status": "blocked",
                    "classification": "tracked_final_resources",
                    "resources_file": {"path": resources_label, "exists": True},
                    "repairs": [],
                    "operator_actions": [
                        "remove services/backend/.local/final-resources.env from git tracking"
                    ],
                    "safety": _safety(writes_final_resources=False),
                }
                return FinalResourceRepairResult(exit_code=1, report=report)

            repaired_text = _repair_text(text)
            selected_resources_file.write_text(repaired_text, encoding="utf-8")
            _chmod_owner_only(selected_resources_file)
            report = {
                "kind": "final_resource_repair_report",
                "status": "repaired",
                "resources_file": {"path": resources_label, "exists": True},
                "summary": {"repaired": len(repairs)},
                "repairs": repairs,
                "operator_actions": ["rerun make final-resource-apply-preview"],
                "safety": _safety(writes_final_resources=True),
            }
            return FinalResourceRepairResult(exit_code=0, report=report)

        report = {
            "kind": "final_resource_repair_report",
            "status": "repairable",
            "resources_file": {"path": resources_label, "exists": True},
            "repairs": repairs,
            "operator_actions": [
                "run make final-resource-repair",
                "rerun make final-resource-apply-preview",
            ],
            "safety": _safety(writes_final_resources=False),
        }
        return FinalResourceRepairResult(exit_code=2, report=report)

    report = {
        "kind": "final_resource_repair_report",
        "status": "ready",
        "resources_file": {"path": resources_label, "exists": True},
        "repairs": [],
        "operator_actions": ["rerun make final-resource-apply-preview"],
        "safety": _safety(writes_final_resources=False),
    }
    return FinalResourceRepairResult(exit_code=0, report=report)


def _repair_text(text: str) -> str:
    repaired_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        line_body = line[:-1] if line.endswith("\n") else line
        line_break = "\n" if line.endswith("\n") else ""
        parsed = _parse_assignment(line_body)
        if parsed is None:
            repaired_lines.append(line)
            continue
        key, value = parsed
        if key == "PRODUCT_BUNDLE_IDENTIFIER" and _is_example_bundle_identifier(value):
            repaired_lines.append(f"{key}={line_break}")
            continue
        if key == "PMF_BACKEND_BASE_URL" and _is_example_backend_url(value):
            repaired_lines.append(f"{key}={line_break}")
            continue
        repaired_lines.append(line)
    return "".join(repaired_lines)


def _repairs_for_text(text: str) -> list[dict[str, Any]]:
    repairs: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        parsed = _parse_assignment(line)
        if parsed is None:
            continue
        key, value = parsed
        if key not in REPAIRABLE_KEYS:
            continue
        if key == "PRODUCT_BUNDLE_IDENTIFIER" and _is_example_bundle_identifier(value):
            repairs.append(_repair_item(key=key, line_number=line_number))
        if key == "PMF_BACKEND_BASE_URL" and _is_example_backend_url(value):
            repairs.append(_repair_item(key=key, line_number=line_number))
    return repairs


def _parse_assignment(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped.removeprefix("export ").strip()
    if "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    return key.strip(), value.strip()


def _repair_item(*, key: str, line_number: int) -> dict[str, Any]:
    return {
        "id": key,
        "line_number": line_number,
        "classification": "placeholder_value",
        "action": "clear_value",
    }


def _is_example_backend_url(value: str) -> bool:
    normalized = value.strip().rstrip("/").lower()
    return normalized in EXAMPLE_BACKEND_BASE_URLS


def _is_example_bundle_identifier(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized == "com.example" or normalized.startswith("com.example.")


def _is_tracked_final_resources(*, repo_root: Path, resources_file: Path) -> bool:
    try:
        relative_path = resources_file.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", relative_path.as_posix()],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _chmod_owner_only(path: Path) -> None:
    try:
        path.chmod(0o600)
    except OSError:
        return


def _path_label(*, path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return "[external-final-resources-file]"


def _safety(*, writes_final_resources: bool) -> dict[str, bool]:
    return {
        "writes_final_resources": writes_final_resources,
        "writes_backend_env": False,
        "writes_ios_deploy_config": False,
        "provider_calls": False,
        "global_mutation": False,
        "provider_secrets_in_report": False,
        "local_paths_in_report": False,
    }


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
