from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Protocol

from myth_forge_api.providers.three_d import ThreeDGenerationRequest, ThreeDSourceImage

REVIEW_RUBRIC = [
    "Artifact silhouette is recognizable",
    "Mythic details match prompt and context",
    "Material language is plausible",
    "Mobile scene variant is present",
    "Printability concerns are visible for later review",
]

MANUAL_REVIEW_EMPTY = {
    "artifact_quality": None,
    "prompt_alignment": None,
    "mobile_readiness": None,
    "printability_signal": None,
    "notes": None,
}


class ThreeDProviderForEvaluation(Protocol):
    provider_name: str

    def generate_game_asset(self, request: ThreeDGenerationRequest):
        ...


@dataclass(frozen=True)
class ThreeDEvaluationCase:
    case_id: str
    category: str
    prompt: str
    expected_input_mode: str
    review_focus: str
    source_images: tuple["ThreeDEvaluationSourceImage", ...] = ()


@dataclass(frozen=True)
class ThreeDEvaluationSourceImage:
    source_id: str
    role: str
    content_type: str
    data_uri: str


DEFAULT_THREE_D_EVALUATION_SUITE = (
    ThreeDEvaluationCase(
        case_id="object_01_brass_key",
        category="object_description",
        prompt=(
            "Create a worn brass key relic with rounded bow, chipped teeth, warm patina, "
            "and hand-polished edges."
        ),
        expected_input_mode="text_prompt",
        review_focus="recognizable key silhouette and worn brass material",
    ),
    ThreeDEvaluationCase(
        case_id="object_02_ceramic_seed_cup",
        category="object_description",
        prompt="Create a small cracked ceramic cup that looks like it protects three glowing seeds inside.",
        expected_input_mode="text_prompt",
        review_focus="cup form, crack detail, contained seed shapes",
    ),
    ThreeDEvaluationCase(
        case_id="object_03_glass_button",
        category="object_description",
        prompt="Create a translucent green glass coat button enlarged into a sacred village artifact.",
        expected_input_mode="text_prompt",
        review_focus="translucent button holes and glass material",
    ),
    ThreeDEvaluationCase(
        case_id="object_04_folded_receipt",
        category="object_description",
        prompt=(
            "Create a folded paper receipt transformed into a tiny altar with embossed "
            "numbers and torn edges."
        ),
        expected_input_mode="text_prompt",
        review_focus="folded paper geometry and readable altar-like silhouette",
    ),
    ThreeDEvaluationCase(
        case_id="context_01_deadline_key",
        category="object_plus_context",
        prompt=(
            "Create a brass key relic for someone under deadline pressure; make it feel "
            "tender, strange, and overused."
        ),
        expected_input_mode="text_prompt",
        review_focus="object plus emotional context alignment",
    ),
    ThreeDEvaluationCase(
        case_id="context_02_new_beginning_plant",
        category="object_plus_context",
        prompt=(
            "Create a desk plant shrine for a new beginning, mixing ceramic pot, living "
            "leaves, and quiet uncertainty."
        ),
        expected_input_mode="text_prompt",
        review_focus="plant, pot, and hopeful but mysterious tone",
    ),
    ThreeDEvaluationCase(
        case_id="context_03_broken_watch",
        category="object_plus_context",
        prompt=(
            "Create a broken wristwatch artifact about recovering time after burnout, with "
            "exposed gears and soft light."
        ),
        expected_input_mode="text_prompt",
        review_focus="watch identity and recovery theme",
    ),
    ThreeDEvaluationCase(
        case_id="context_04_pocket_stone",
        category="object_plus_context",
        prompt=(
            "Create a smooth pocket stone relic carried during a move to a new city, with "
            "map-like veins across it."
        ),
        expected_input_mode="text_prompt",
        review_focus="stone material and migration symbolism",
    ),
    ThreeDEvaluationCase(
        case_id="myth_01_small_door_keeper",
        category="mythic_prompt",
        prompt=(
            "Create The Keeper of the Small Door, a hand-sized brass key idol worshiped "
            "by a village of cautious archivists."
        ),
        expected_input_mode="text_prompt",
        review_focus="myth title translated into inspectable 3D object",
    ),
    ThreeDEvaluationCase(
        case_id="myth_02_lantern_of_second_thoughts",
        category="mythic_prompt",
        prompt=(
            "Create The Lantern of Second Thoughts, a pocket lantern with soot, blue glass, "
            "and three quiet handles."
        ),
        expected_input_mode="text_prompt",
        review_focus="lantern readability and unusual mythic details",
    ),
    ThreeDEvaluationCase(
        case_id="myth_03_spoon_that_remembers",
        category="mythic_prompt",
        prompt=(
            "Create The Spoon That Remembers, a bent silver spoon with etched village "
            "scenes along the bowl."
        ),
        expected_input_mode="text_prompt",
        review_focus="spoon shape plus engraved narrative surface",
    ),
    ThreeDEvaluationCase(
        case_id="myth_04_threaded_moon",
        category="mythic_prompt",
        prompt=(
            "Create The Threaded Moon, a crescent charm wrapped in red thread, wax seals, "
            "and small hanging bells."
        ),
        expected_input_mode="text_prompt",
        review_focus="crescent charm and attached details",
    ),
    ThreeDEvaluationCase(
        case_id="material_01_translucent_shell",
        category="material_stress",
        prompt=(
            "Create a translucent shell relic with pearl interior, chipped rim, wet "
            "highlights, and carved tally marks."
        ),
        expected_input_mode="text_prompt",
        review_focus="transparent shell material and carved marks",
    ),
    ThreeDEvaluationCase(
        case_id="material_02_rusted_iron_ribbon",
        category="material_stress",
        prompt=(
            "Create a rusted iron ribbon twisted around a small mirror shard, with "
            "corrosion, reflection, and dents."
        ),
        expected_input_mode="text_prompt",
        review_focus="mixed rusted metal and mirror material",
    ),
    ThreeDEvaluationCase(
        case_id="material_03_fabric_knot",
        category="material_stress",
        prompt=(
            "Create a knotted blue fabric talisman with frayed threads, stitched symbols, "
            "and a wooden bead core."
        ),
        expected_input_mode="text_prompt",
        review_focus="fabric folds, fraying, and bead core",
    ),
    ThreeDEvaluationCase(
        case_id="material_04_wax_sealed_card",
        category="material_stress",
        prompt=(
            "Create a thick card sealed with red wax, pressed thumbprint, curled corners, "
            "and a brass pin."
        ),
        expected_input_mode="text_prompt",
        review_focus="paper, wax, and pin material separation",
    ),
    ThreeDEvaluationCase(
        case_id="print_01_thumb_sized_totem",
        category="printability_probe",
        prompt=(
            "Create a thumb-sized totem with one stable flat base, bold carved face, and "
            "no fragile thin spikes."
        ),
        expected_input_mode="text_prompt",
        review_focus="simple printable silhouette and stable base",
    ),
    ThreeDEvaluationCase(
        case_id="print_02_ring_relic",
        category="printability_probe",
        prompt="Create a small ring relic with thick band, raised symbols, and a single inset moon stone.",
        expected_input_mode="text_prompt",
        review_focus="ring topology and print-friendly raised detail",
    ),
    ThreeDEvaluationCase(
        case_id="print_03_tabletop_shrine",
        category="printability_probe",
        prompt="Create a tabletop shrine token with stepped base, central arch, and three chunky candles.",
        expected_input_mode="text_prompt",
        review_focus="stable miniature shrine with printable candles",
    ),
    ThreeDEvaluationCase(
        case_id="print_04_coin_of_return",
        category="printability_probe",
        prompt=(
            "Create a thick coin relic called the Coin of Return with raised rim, deep "
            "symbol grooves, and worn edge marks."
        ),
        expected_input_mode="text_prompt",
        review_focus="coin relief depth and printability signal",
    ),
)

SYNTHETIC_PNG_DATA_URIS = {
    "front": (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    ),
    "side": (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    ),
    "top": (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    ),
    "detail": (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    ),
}


def _synthetic_source(role: str) -> ThreeDEvaluationSourceImage:
    return ThreeDEvaluationSourceImage(
        source_id=role,
        role=role,
        content_type="image/png",
        data_uri=SYNTHETIC_PNG_DATA_URIS[role],
    )


GUIDED_SCAN_SMOKE_EVALUATION_SUITE = (
    ThreeDEvaluationCase(
        case_id="scan_01_single_reference_key",
        category="guided_scan_smoke",
        prompt=(
            "Create a worn brass key relic from a single guided scan reference, preserving "
            "the broad bow, chipped teeth, and handheld scale."
        ),
        expected_input_mode="single_image",
        review_focus="single-image source routing and recognizable key silhouette",
        source_images=(_synthetic_source("front"),),
    ),
    ThreeDEvaluationCase(
        case_id="scan_02_two_angle_key",
        category="guided_scan_smoke",
        prompt=(
            "Create a worn brass key relic from front and side guided scan references, "
            "preserving thickness, teeth, and patina."
        ),
        expected_input_mode="multi_image",
        review_focus="two-image source routing and stronger depth cues",
        source_images=(_synthetic_source("front"), _synthetic_source("side")),
    ),
    ThreeDEvaluationCase(
        case_id="scan_03_four_angle_key",
        category="guided_scan_smoke",
        prompt=(
            "Create a worn brass key relic from front, side, top, and detail guided scan "
            "references, emphasizing readable teeth and hand-polished wear."
        ),
        expected_input_mode="multi_image",
        review_focus="four-image source routing and capped provider media selection",
        source_images=(
            _synthetic_source("front"),
            _synthetic_source("side"),
            _synthetic_source("top"),
            _synthetic_source("detail"),
        ),
    ),
)


def build_custom_prompt_cases(prompts: list[str]) -> tuple[ThreeDEvaluationCase, ...]:
    return tuple(
        ThreeDEvaluationCase(
            case_id=f"custom_{index:03d}",
            category="custom_prompt",
            prompt=prompt,
            expected_input_mode="text_prompt",
            review_focus="custom prompt review",
        )
        for index, prompt in enumerate(prompts, start=1)
    )


def run_three_d_evaluation(
    *,
    provider: ThreeDProviderForEvaluation,
    selected_provider: str,
    suite_name: str,
    cases: tuple[ThreeDEvaluationCase, ...],
) -> dict[str, object]:
    case_reports = [_run_case(provider, case) for case in cases]
    succeeded = sum(1 for case in case_reports if case["status"] == "succeeded")
    failed = sum(1 for case in case_reports if case["status"] == "failed")
    return _sanitize_report(
        {
            "kind": "three_d_evaluation_report",
            "status": "failed" if failed else "succeeded",
            "suite": suite_name,
            "provider": selected_provider,
            "total_cases": len(cases),
            "succeeded": succeeded,
            "failed": failed,
            "coverage": _coverage(case_reports),
            "review_rubric": REVIEW_RUBRIC,
            "safety": {
                "raw_media_in_report": False,
                "provider_secrets_in_report": False,
                "local_paths_in_report": False,
            },
            "cases": case_reports,
        }
    )


def _run_case(
    provider: ThreeDProviderForEvaluation,
    evaluation_case: ThreeDEvaluationCase,
) -> dict[str, object]:
    started_at = time.perf_counter()
    provider_source_images = tuple(
        ThreeDSourceImage(
            uri=f"evaluation-source://{evaluation_case.case_id}/{source_image.source_id}",
            content_type=source_image.content_type,
            data_uri=source_image.data_uri,
        )
        for source_image in evaluation_case.source_images
    )
    base_report = {
        "case_id": evaluation_case.case_id,
        "category": evaluation_case.category,
        "prompt": evaluation_case.prompt,
        "expected_input_mode": evaluation_case.expected_input_mode,
        "review_focus": evaluation_case.review_focus,
        "source_image_count": len(evaluation_case.source_images),
        "source_image_roles": [source_image.role for source_image in evaluation_case.source_images],
        "manual_review": dict(MANUAL_REVIEW_EMPTY),
    }
    try:
        asset = provider.generate_game_asset(
            ThreeDGenerationRequest(
                session_id=_session_id_for_case(evaluation_case.case_id),
                prompt=evaluation_case.prompt,
                source_images=provider_source_images,
            )
        )
        variant_roles = [variant.role for variant in asset.variants]
        generation_provenance = (
            asset.generation_provenance.model_dump(mode="json")
            if asset.generation_provenance is not None
            else None
        )
        return {
            **base_report,
            "status": "succeeded",
            "provider": asset.provider,
            "asset_uri": asset.uri,
            "asset_format": asset.format,
            "variant_roles": variant_roles,
            "scene_loadable_variant": any(variant.is_scene_loadable for variant in asset.variants),
            "generation_provenance": generation_provenance,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": None,
        }
    except Exception as exc:
        return {
            **base_report,
            "status": "failed",
            "provider": provider.provider_name,
            "asset_uri": None,
            "asset_format": None,
            "variant_roles": [],
            "scene_loadable_variant": False,
            "generation_provenance": None,
            "elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "error": _safe_text(str(exc)),
        }


def _coverage(case_reports: list[dict[str, object]]) -> dict[str, object]:
    input_modes = {"text_prompt": 0, "single_image": 0, "multi_image": 0, "unknown": 0}
    variant_roles: dict[str, int] = {}
    scene_loadable_cases = 0
    for case_report in case_reports:
        provenance = case_report.get("generation_provenance")
        input_mode = "unknown"
        if isinstance(provenance, dict):
            input_mode_value = provenance.get("input_mode")
            if isinstance(input_mode_value, str) and input_mode_value in input_modes:
                input_mode = input_mode_value
        input_modes[input_mode] += 1
        roles = case_report.get("variant_roles")
        if isinstance(roles, list):
            for role in roles:
                if isinstance(role, str):
                    variant_roles[role] = variant_roles.get(role, 0) + 1
        if case_report.get("scene_loadable_variant") is True:
            scene_loadable_cases += 1
    return {
        "input_modes": input_modes,
        "variant_roles": variant_roles,
        "scene_loadable_cases": scene_loadable_cases,
    }


def _session_id_for_case(case_id: str) -> str:
    safe_case_id = re.sub(r"[^A-Za-z0-9_-]+", "_", case_id).strip("_").lower()
    return f"eval_{safe_case_id[:48]}"


def _sanitize_report(report: dict[str, object]) -> dict[str, object]:
    return json.loads(json.dumps(_sanitize_value(report)))


def _sanitize_value(value):
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    return value


def _safe_text(message: str) -> str:
    replacements = [
        r"Authorization\s*[=:]\s*Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"Bearer\s+[A-Za-z0-9._~+/\-=:-]+",
        r"raw=[^\s,;\"']+",
        r"api[_-]?key\s*[=:]\s*[^\s,;\"']+",
        r"data:[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/=_-]+",
        r"file://[^\s,;\"']+",
    ]
    sanitized = message
    for pattern in replacements:
        sanitized = re.sub(pattern, "[redacted]", sanitized, flags=re.IGNORECASE)
    return sanitized
