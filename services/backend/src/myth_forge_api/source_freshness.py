from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRODUCT_SOURCE_PATHS = (
    "Makefile",
    "services/backend/pyproject.toml",
    "services/backend/src",
    "services/backend/tests",
    "services/backend/scripts",
    "apps/mobile/ios",
    "packages",
)


@dataclass(frozen=True)
class GitProductSourceMetadata:
    revision: str | None
    committed_at_epoch: float
    source_scope: dict[str, Any]


def git_product_source_metadata(repo_root: Path) -> GitProductSourceMetadata | None:
    try:
        revision = _git_output(
            repo_root,
            [
                "git",
                "-C",
                str(repo_root),
                "log",
                "-1",
                "--format=%h",
                "--",
                *PRODUCT_SOURCE_PATHS,
            ],
        )
        committed_at = _git_output(
            repo_root,
            [
                "git",
                "-C",
                str(repo_root),
                "log",
                "-1",
                "--format=%ct",
                "--",
                *PRODUCT_SOURCE_PATHS,
            ],
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if not committed_at:
        return None
    try:
        committed_at_epoch = float(committed_at)
    except ValueError:
        return None
    return GitProductSourceMetadata(
        revision=revision or None,
        committed_at_epoch=committed_at_epoch,
        source_scope={
            "kind": "git_product_sources",
            "paths": list(PRODUCT_SOURCE_PATHS),
        },
    )


def freshness_payload(
    *,
    status: str,
    classification: str,
    source_modified_at: float | None,
    git_metadata: GitProductSourceMetadata | None,
    checked_against: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "classification": classification,
        "checked_against": checked_against,
        "source_modified_at": _iso_timestamp(source_modified_at),
        "current_revision": None if git_metadata is None else git_metadata.revision,
        "current_revision_committed_at": None
        if git_metadata is None
        else _iso_timestamp(git_metadata.committed_at_epoch),
    }
    if git_metadata is not None:
        payload["source_scope"] = git_metadata.source_scope
    return payload


def _git_output(repo_root: Path, command: list[str]) -> str:
    return subprocess.run(
        command,
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=2,
    ).stdout.strip()


def _iso_timestamp(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return (
        datetime.fromtimestamp(epoch, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
