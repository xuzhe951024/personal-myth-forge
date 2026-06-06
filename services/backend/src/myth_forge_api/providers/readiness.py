from __future__ import annotations

from myth_forge_api.config import Settings
from myth_forge_api.domain.models import ProviderReadinessItem, ProviderReadinessResponse


def build_provider_readiness(settings: Settings) -> ProviderReadinessResponse:
    providers = [
        _three_d_readiness(settings),
        _npc_readiness(settings),
        _print_readiness(settings),
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


def _print_readiness(settings: Settings) -> ProviderReadinessItem:
    selected_provider = settings.print_provider
    if selected_provider == "local":
        return ProviderReadinessItem(
            kind="print",
            selected_provider="local",
            status="local_stub",
            is_demo_ready=True,
            is_real_provider_ready=False,
            capabilities=["print_candidate_stub", "quote_stub", "manual_review_required"],
            notes=[
                "Local print quote provider is deterministic and demo-ready.",
                "Select PRINT_PROVIDER=treatstock or sculpteo after live quote adapters are implemented.",
            ],
        )
    if selected_provider == "treatstock":
        if not settings.treatstock_api_key:
            return ProviderReadinessItem(
                kind="print",
                selected_provider="treatstock",
                status="missing_configuration",
                is_demo_ready=False,
                is_real_provider_ready=False,
                missing_env=["TREATSTOCK_API_KEY"],
                capabilities=["quote_api_key_slot", "order_handoff_future"],
                notes=[
                    "TREATSTOCK_API_KEY is required for future Treatstock quote integration."
                ],
            )
        return ProviderReadinessItem(
            kind="print",
            selected_provider="treatstock",
            status="ready",
            is_demo_ready=True,
            is_real_provider_ready=True,
            capabilities=[
                "url_upload_quote",
                "minimum_price_quote",
                "checkout_handoff",
                "manual_review_required",
            ],
            notes=[
                "Treatstock is configured for live print quote handoff.",
                "Order placement still requires separate user approval and shipping data.",
            ],
        )
    if selected_provider == "sculpteo":
        missing = [] if settings.sculpteo_api_key else ["SCULPTEO_API_KEY"]
        return ProviderReadinessItem(
            kind="print",
            selected_provider="sculpteo",
            status="not_implemented" if not missing else "missing_configuration",
            is_demo_ready=False,
            is_real_provider_ready=False,
            missing_env=missing,
            capabilities=["quote_api_key_slot", "order_handoff_future"],
            notes=["Sculpteo live quote adapter is not implemented yet."],
        )
    return ProviderReadinessItem(
        kind="print",
        selected_provider=selected_provider,
        status="unsupported",
        is_demo_ready=False,
        is_real_provider_ready=False,
        capabilities=[],
        notes=[f"Unsupported PRINT_PROVIDER value: {selected_provider}."],
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
