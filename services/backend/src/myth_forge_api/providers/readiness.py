from __future__ import annotations

from myth_forge_api.config import Settings
from myth_forge_api.domain.models import ProviderReadinessItem, ProviderReadinessResponse


def build_provider_readiness(settings: Settings) -> ProviderReadinessResponse:
    providers = [
        _three_d_readiness(settings),
        _npc_readiness(settings),
        _print_readiness(),
        _capture_storage_readiness(),
    ]
    return ProviderReadinessResponse(
        overall_demo_ready=all(item.is_demo_ready for item in providers),
        overall_real_ready=all(item.is_real_provider_ready for item in providers),
        providers=providers,
    )


def _three_d_readiness(settings: Settings) -> ProviderReadinessItem:
    selected_provider = settings.three_d_provider
    if selected_provider == "local":
        return ProviderReadinessItem(
            kind="three_d",
            selected_provider="local",
            status="local_stub",
            is_demo_ready=True,
            is_real_provider_ready=False,
            capabilities=["text_to_3d_stub", "image_source_contract", "asset_variant_stub"],
            notes=[
                "Local 3D provider is deterministic and demo-ready.",
                "Select THREE_D_PROVIDER=meshy and provide a Meshy key for real 3D generation.",
            ],
        )
    if selected_provider == "meshy":
        if settings.meshy_api_key:
            return ProviderReadinessItem(
                kind="three_d",
                selected_provider="meshy",
                status="ready",
                is_demo_ready=True,
                is_real_provider_ready=True,
                capabilities=["text_to_3d", "image_to_3d_jpeg_png", "glb", "usdz_variant"],
                notes=[
                    "Meshy is configured for real 3D generation.",
                    "HEIC/HEIF-only guided scans still fall back until transcoding exists.",
                ],
            )
        return ProviderReadinessItem(
            kind="three_d",
            selected_provider="meshy",
            status="missing_configuration",
            is_demo_ready=False,
            is_real_provider_ready=False,
            missing_env=["MESHY_API_KEY"],
            capabilities=["text_to_3d", "image_to_3d_jpeg_png", "glb", "usdz_variant"],
            notes=["MESHY_API_KEY is required when THREE_D_PROVIDER=meshy."],
        )
    return ProviderReadinessItem(
        kind="three_d",
        selected_provider=selected_provider,
        status="unsupported",
        is_demo_ready=False,
        is_real_provider_ready=False,
        capabilities=[],
        notes=[f"Unsupported THREE_D_PROVIDER value: {selected_provider}."],
    )


def _npc_readiness(settings: Settings) -> ProviderReadinessItem:
    selected_provider = settings.npc_provider
    if selected_provider == "local":
        return ProviderReadinessItem(
            kind="npc",
            selected_provider="local",
            status="local_stub",
            is_demo_ready=True,
            is_real_provider_ready=False,
            capabilities=[
                "deterministic_agent_traces",
                "deterministic_agent_ticks",
                "world_arbitration_handoff",
            ],
            notes=[
                "Local NPC runtime is deterministic and demo-ready.",
                "Select NPC_PROVIDER=openai and provide an OpenAI key for AI-driven NPC traces.",
            ],
        )
    if selected_provider == "openai":
        if settings.openai_api_key:
            return ProviderReadinessItem(
                kind="npc",
                selected_provider="openai",
                status="ready",
                is_demo_ready=True,
                is_real_provider_ready=True,
                capabilities=[
                    "structured_agent_traces",
                    "structured_agent_ticks",
                    "npc_reactions",
                    "world_handoff",
                ],
                notes=[
                    "OpenAI NPC provider is configured for AI-driven NPC traces and stateless ticks."
                ],
            )
        return ProviderReadinessItem(
            kind="npc",
            selected_provider="openai",
            status="missing_configuration",
            is_demo_ready=False,
            is_real_provider_ready=False,
            missing_env=["OPENAI_API_KEY"],
            capabilities=[
                "structured_agent_traces",
                "structured_agent_ticks",
                "npc_reactions",
                "world_handoff",
            ],
            notes=["OPENAI_API_KEY is required when NPC_PROVIDER=openai for traces and ticks."],
        )
    return ProviderReadinessItem(
        kind="npc",
        selected_provider=selected_provider,
        status="unsupported",
        is_demo_ready=False,
        is_real_provider_ready=False,
        capabilities=[],
        notes=[f"Unsupported NPC_PROVIDER value: {selected_provider}."],
    )


def _print_readiness() -> ProviderReadinessItem:
    return ProviderReadinessItem(
        kind="print",
        selected_provider="local_stub",
        status="local_stub",
        is_demo_ready=True,
        is_real_provider_ready=False,
        capabilities=["print_candidate_stub", "manual_review_required"],
        notes=[
            "Print candidate generation is local and demo-ready.",
            "Treatstock/Sculpteo fulfillment adapters are not implemented yet.",
        ],
    )


def _capture_storage_readiness() -> ProviderReadinessItem:
    return ProviderReadinessItem(
        kind="capture_storage",
        selected_provider="local_filesystem",
        status="ready",
        is_demo_ready=True,
        is_real_provider_ready=True,
        capabilities=["local_capture_manifest", "local_media_payload_read"],
        notes=[
            "Capture storage is configured for local development.",
            "The readiness response does not expose the absolute storage path.",
        ],
    )
