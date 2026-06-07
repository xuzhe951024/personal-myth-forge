from __future__ import annotations

LEGACY_FINAL_RESOURCE_COPY_MARKERS = (
    "services/backend/final-resources.env.example",
    "services/backend/.local/final-resources.env",
)
NORMALIZED_FINAL_RESOURCE_INIT_ACTION = "run make final-resource-init"


def normalize_operator_action(action: str) -> str:
    normalized = action.strip()
    if all(marker in normalized for marker in LEGACY_FINAL_RESOURCE_COPY_MARKERS):
        return NORMALIZED_FINAL_RESOURCE_INIT_ACTION
    if normalized.endswith(f": {NORMALIZED_FINAL_RESOURCE_INIT_ACTION}"):
        return NORMALIZED_FINAL_RESOURCE_INIT_ACTION
    return normalized
