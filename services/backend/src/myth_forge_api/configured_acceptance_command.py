from __future__ import annotations

CONFIGURED_FINAL_ACCEPTANCE_COMMAND = "make final-acceptance-configured"
CONFIGURED_FINAL_ACCEPTANCE_OUTPUT = (
    "services/backend/.local/final-acceptance-configured.json"
)
CONFIGURED_FINAL_ACCEPTANCE_COST_REVIEW_ACTION = (
    "run make final-acceptance-configured only after live provider cost review "
    "and --allow-live-provider-calls consent"
)
