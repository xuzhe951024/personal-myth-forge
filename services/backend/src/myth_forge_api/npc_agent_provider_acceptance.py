from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceRequirement:
    file: str
    contains: str


@dataclass(frozen=True)
class FeatureRequirement:
    id: str
    label: str
    requirements: tuple[SourceRequirement, ...]


@dataclass(frozen=True)
class NPCAgentProviderAcceptanceResult:
    exit_code: int
    report: dict[str, Any]


FEATURES = (
    FeatureRequirement(
        id="openai_director_structured_output",
        label="OpenAI NPC director structured output",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc.py",
                "OpenAINPCDirector",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc.py",
                "OpenAINPCOutput",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc.py",
                "text_format=OpenAINPCOutput",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc.py",
                'agent_runtime="openai_structured_runtime"',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc.py",
                "OPENAI_API_KEY is required for NPC generation.",
            ),
        ),
    ),
    FeatureRequirement(
        id="openai_tick_structured_output",
        label="OpenAI NPC tick structured output",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc_ticks.py",
                "OpenAINPCTickRuntime",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc_ticks.py",
                "OpenAINPCTickOutput",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc_ticks.py",
                'runtime_name = "openai_tick_structured_runtime"',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc_ticks.py",
                "text_format=OpenAINPCTickOutput",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/npc_ticks.py",
                "OPENAI_API_KEY is required for NPC tick generation.",
            ),
        ),
    ),
    FeatureRequirement(
        id="provider_factory_wiring",
        label="NPC provider factory wiring",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/factory.py",
                'npc_provider == "openai"',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/factory.py",
                "OpenAINPCDirector.from_settings",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/factory.py",
                "OpenAINPCTickRuntime.from_settings",
            ),
        ),
    ),
    FeatureRequirement(
        id="provider_readiness_contract",
        label="NPC provider readiness contract",
        requirements=(
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/readiness.py",
                "structured_agent_traces",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/readiness.py",
                "structured_agent_ticks",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/readiness.py",
                'missing_env=["OPENAI_API_KEY"]',
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/providers/readiness.py",
                "OpenAI NPC provider is configured for AI-driven NPC traces and stateless ticks.",
            ),
        ),
    ),
    FeatureRequirement(
        id="resource_handoff_contract",
        label="NPC resource handoff contract",
        requirements=(
            SourceRequirement("services/backend/src/myth_forge_api/resource_handoff.py", "NPC_PROVIDER"),
            SourceRequirement("services/backend/src/myth_forge_api/resource_handoff.py", "OPENAI_API_KEY"),
            SourceRequirement(
                "services/backend/src/myth_forge_api/resource_handoff.py",
                "AI Agent NPC traces and ticks",
            ),
            SourceRequirement(
                "services/backend/src/myth_forge_api/resource_handoff.py",
                "Backend-only key; mobile sees only generated NPC state.",
            ),
        ),
    ),
    FeatureRequirement(
        id="backend_docs_contract",
        label="Backend OpenAI NPC docs",
        requirements=(
            SourceRequirement("README.md", "NPC_PROVIDER=openai"),
            SourceRequirement("README.md", "OPENAI_API_KEY"),
            SourceRequirement("README.md", "OpenAINPCDirector"),
            SourceRequirement("README.md", "OpenAINPCTickRuntime"),
            SourceRequirement("README.md", "no OpenAI key is stored in or sent to the iOS app"),
        ),
    ),
    FeatureRequirement(
        id="mobile_docs_contract",
        label="Mobile OpenAI NPC docs",
        requirements=(
            SourceRequirement("apps/mobile/README.md", "P0.23 OpenAI NPC Tick Provider"),
            SourceRequirement("apps/mobile/README.md", "NPC_PROVIDER=openai"),
            SourceRequirement("apps/mobile/README.md", "openai_tick_structured_runtime"),
            SourceRequirement("apps/mobile/README.md", "provider keys"),
        ),
    ),
)


def run_npc_agent_provider_acceptance(
    *,
    repo_root: str | Path | None = None,
) -> NPCAgentProviderAcceptanceResult:
    selected_repo_root = Path(repo_root) if repo_root is not None else _default_repo_root()
    feature_reports = [_feature_report(selected_repo_root, feature) for feature in FEATURES]
    failed = sum(1 for feature in feature_reports if feature["status"] == "failed")
    report = {
        "kind": "npc_agent_provider_acceptance_report",
        "status": "succeeded" if failed == 0 else "failed",
        "summary": {"passed": len(feature_reports) - failed, "failed": failed},
        "required_features": feature_reports,
        "safety": {
            "provider_calls": False,
            "provider_secrets_in_report": False,
            "local_paths_in_report": False,
            "raw_media_in_report": False,
            "payment_links_in_report": False,
        },
    }
    sanitized_report = _sanitize_report(report, selected_repo_root)
    sanitized_report["safety"] = _safety_summary(sanitized_report, selected_repo_root)
    return NPCAgentProviderAcceptanceResult(
        exit_code=0 if failed == 0 else 1,
        report=sanitized_report,
    )


def _feature_report(repo_root: Path, feature: FeatureRequirement) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for requirement in feature.requirements:
        source = _read_source(repo_root / requirement.file)
        if requirement.contains not in source:
            missing.append(
                {
                    "file": requirement.file,
                    "contains": requirement.contains,
                }
            )
    return {
        "id": feature.id,
        "label": feature.label,
        "status": "passed" if not missing else "failed",
        "missing": missing,
    }


def _read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _sanitize_report(report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    text = json.dumps(report)
    text = text.replace(str(repo_root), "[repo-root]")
    text = text.replace(str(Path.home()), "[home]")
    text = re.sub(r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._:-]+", "[redacted]", text)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._:-]+", "[redacted]", text)
    text = re.sub(r"sk-[A-Za-z0-9_-]+", "[redacted]", text)
    text = re.sub(r"api[_-]?key\s*[=:]\s*[^\s,;]+", "[redacted]", text, flags=re.IGNORECASE)
    text = re.sub(r"data:image/[^\"\\\s]+", "[redacted-media]", text)
    text = re.sub(r"https?://(?:pay|checkout)\.[^\"\\\s]+", "[redacted-payment-link]", text)
    return json.loads(text)


def _safety_summary(report: dict[str, Any], repo_root: Path) -> dict[str, bool]:
    text = json.dumps(report)
    return {
        "provider_calls": False,
        "provider_secrets_in_report": bool(
            re.search(
                r"sk-[A-Za-z0-9_-]+|Authorization\s*[=:]\s*Bearer|Bearer\s+",
                text,
            )
        ),
        "local_paths_in_report": str(repo_root) in text or str(Path.home()) in text or "file://" in text,
        "raw_media_in_report": "data:image" in text or "local-capture://" in text,
        "payment_links_in_report": bool(re.search(r"https?://(?:pay|checkout)\.", text)),
    }
